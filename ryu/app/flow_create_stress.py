# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.app.simple_switch_13 import SimpleSwitch13
import time
import logging

#ipRange() from http://cmikavac.net/2011/09/11/how-to-generate-an-ip-range-list-in-python/
def ipRange(start_ip, end_ip):
   start = list(map(int, start_ip.split(".")))
   end = list(map(int, end_ip.split(".")))
   temp = start
   ip_range = []
   
   ip_range.append(start_ip)
   while temp != end:
      start[3] += 1
      for i in (3, 2, 1):
         if temp[i] == 256:
            temp[i] = 0
            temp[i-1] += 1
      ip_range.append(".".join(map(str, temp)))    
      
   return ip_range
   
   
class stressTest(SimpleSwitch13):

    def __init__(self, *args, **kwargs):
        super(stressTest, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        super(stressTest, self).switch_features_handler(ev)

        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        ip_range = ipRange("10.0.0.1", "10.1.0.1")
        print 'Pushing ',len(ip_range),' flows'
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        start_time=time.time()
        lap_time=start_time
        count = 0
        nf = 10000
        for ip in ip_range:
             match = parser.OFPMatch(ipv4_src=ip)
             self.add_flow(datapath, 0, match, actions)
             count += 1
             if count%nf == 0:
                   duration = time.time() - lap_time
                   print nf, ' flows in ', duration, ' seconds, rate=', nf/duration
                   lap_time = time.time()
        duration = time.time()-start_time     
        print 'In ',duration,' seconds'
        print 'Rate is ', len(ip_range)/duration, ' flows/second'

