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

    def initialize(self, power_supply, initial_current):
        '''initialize configuration'''

        # reset device
        self.dev.write('*rst; status:preset; *cls')
        # decouple the output ports
        self.dev.write('instrument:couple:output:state none')
        # set protection voltage
        self.dev.write("voltage:protection:level 4.5;state on")
        # set output1 voltage for powering on the mobile
        self.dev.write("voltage1 %f" % power_supply)
        # enable the output 1
        self.dev.write("output1 on")
        # set output2 voltage as 1V. for current-detect resistance
        self.dev.write("voltage2 1")
        # set current of output2
        self.set_current(initial_current)
        # enable the output 2
        self.dev.write("output2 on")
        # enable panel display
        self.dev.write("display on")
        # display channel info
        self.dev.write("display:channel 2")

    def set_current(self, current):
        '''set current value'''

        # output2 is used as simulating ntc
        self.dev.write("current2 %s MA" % current)
        return self.dev.query("current2?")


def preprocess():
    '''create instances for testcase'''

    # get configuration from XML
    config_tree = ET.parse('config.xml')
    root = config_tree.getroot()
    t_delay = float(root.find('delay').text)

    # get expected current params
    current = root.find("current")
    initial_current = int(current.attrib['initial'])
    final_current = int(current.attrib['final'])
    step_current = int(current.attrib['step'])

    # get power supply voltage
    power_supply = float(root.find("supply").text)

    # create dc_source instance
    rm = visa.ResourceManager('visa32.dll')
    dev_list = rm.list_resources()
    dev = rm.open_resource(dev_list[0])
    dc_source = DCSource(dev)

    return dc_source, initial_current, final_current, step_current, power_supply, t_delay


def change_current(dc_source, initial_current, final_current, step_current, t_delay):

    if initial_current < final_current:
        direction = 1
    else:
        direction = -1

    step_current = direction * abs(step_current)
    for current in range(initial_current, final_current+step_current, step_current):
        i = int(float(dc_source.set_current(current)) * 1000)
        logging.info('-------------------------Set current %smA-------------------------' % i)
        time.sleep(t_delay)


def testcase(dc_source, initial_current, final_current, step_current, power_supply, t_delay):

    # config log pattern
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S')

    # initialize dc source and wait
    dc_source.initialize(power_supply, initial_current)
    raw_input("press 'enter' to start test:")

    change_current(dc_source, initial_current, final_current, step_current, t_delay)


if __name__ == '__main__':

    dc_source, initial_current, final_current, step_current, power_supply, t_delay = preprocess()
    testcase(dc_source, initial_current, final_current, step_current, power_supply, t_delay)