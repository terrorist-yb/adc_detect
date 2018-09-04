# -*- coding: utf-8 _*_

###############################################################################
# Copyright (C), 2018, TP-LINK Technologies Co., Ltd.
#
# Author: wuyangbo_w9477
# History:
# 1, 2018-01-17, wuyangbo, first create:current adc detect
###############################################################################
import visa
import time
import logging
import xml.etree.ElementTree as ET

class DCSource(object):
    '''dc source operation model'''

    def __init__(self, dev):
        '''create gpib instrument instance using visa lib'''

        try:
            if not dev.__class__.__name__ in ['GPIBInstrument']:
                raise ValueError
        except ValueError:
            print 'Instrument instantiation failed!'
            exit()

        self.dev = dev

    def initialize(self, initial_voltage):
        '''initialize configuration'''

        # reset device
        self.dev.write('*rst; status:preset; *cls')
        # set protection voltage
        self.dev.write("voltage:protection:level 4.5;state on")
        # set output1 voltage
        self.set_voltage(initial_voltage)
        # enable the output 1
        self.dev.write("output on")
        # enable panel display
        self.dev.write("display on")

    def set_voltage(self, voltage):
        '''set current value'''

        self.dev.write("voltage1 %smV" % voltage)
        return self.dev.query("measure:voltage?")


def preprocess():
    '''create instances for testcase'''

    # get configuration from XML
    config_tree = ET.parse('config.xml')
    root = config_tree.getroot()
    t_delay = float(root.find('delay').text)

    # get expected current params
    voltage = root.find("voltage")
    initial_voltage = int(voltage.attrib['initial'])
    final_voltage = int(voltage.attrib['final'])
    step_voltage = int(voltage.attrib['step'])

    # create dc_source instance
    rm = visa.ResourceManager('visa32.dll')
    dev_list = rm.list_resources()
    dev = rm.open_resource(dev_list[0])
    dc_source = DCSource(dev)

    return dc_source, initial_voltage, final_voltage, step_voltage, t_delay


def change_current(dc_source, initial_voltage, final_voltage, step_voltage, t_delay):

    if initial_voltage < final_voltage:
        direction = 1
    else:
        direction = -1

    step_voltage = direction * abs(step_voltage)
    for voltage in range(initial_voltage, final_voltage+step_voltage, step_voltage):
        v = int(float(dc_source.set_voltage(voltage)) * 1000)
        logging.info('-------------------------Set voltage %smV-------------------------' % v)
        time.sleep(t_delay)


def testcase(dc_source, initial_voltage, final_voltage, step_voltage, t_delay):

    # config log pattern
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S')

    # initialize dc source and wait
    dc_source.initialize(initial_voltage)
    raw_input("press 'enter' to start test:")

    change_current(dc_source, initial_voltage, final_voltage, step_voltage, t_delay)


if __name__ == '__main__':
    dc_source, initial_voltage, final_voltage, step_voltage, t_delay = preprocess()
    testcase(dc_source, initial_voltage, final_voltage, step_voltage, t_delay)