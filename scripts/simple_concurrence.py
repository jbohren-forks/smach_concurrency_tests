#!/usr/bin/env python

import rospy
import smach
import smach_ros
from time import sleep

class Work(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['work_succeeded', 'work_failed', 'work_preempted'])

    def execute(self, userdata):
        print 'Executing work'
        while True:
            if self.preempt_requested():
                print "work preempted"
                self.service_preempt()
                return 'work_preempted'
            
            sleep(1)
        return 'work_succeeded'

def main():
    rospy.init_node('smach_simple_concurrence_state_machine')
    
    # Create a SMACH state machine
    sm = smach.StateMachine(outcomes=['succeeded', 'aborted', 'preempted'])
    # Open the container
    with sm:
        sm_active = smach.Concurrence(outcomes=['succeeded', 'aborted', 'preempted'], 
                                      default_outcome='preempted', 
                                      outcome_map={'succeeded':{'WORK':'succeeded', 'MORE_WORK':'succeeded'}, 
                                                   'aborted':{'WORK':'aborted', 'MORE_WORK':'aborted'}, 
                                                   'preempted':{'WORK':'preempted', 'MORE_WORK':'preempted'}})
        with sm_active:
            sm_work1 = smach.StateMachine(outcomes=['succeeded', 'preempted', 'aborted'])
            with sm_work1:
                smach.StateMachine.add('DO_SOME_STUFF', Work(),
                                       transitions = {'work_succeeded':'succeeded', 'work_failed':'aborted', 'work_preempted':'preempted'})
            sm_work2 = smach.StateMachine(outcomes=['succeeded', 'preempted', 'aborted'])
            with sm_work2:
                smach.StateMachine.add('DO_MORE_STUFF', Work(),
                                       transitions={'work_succeeded':'succeeded', 'work_failed':'aborted', 'work_preempted':'preempted'})

            smach.Concurrence.add('WORK', sm_work1)
            smach.Concurrence.add('MORE_WORK', sm_work2) 

        smach.StateMachine.add('ACTIVE', sm_active,
                                transitions={'succeeded':'succeeded', 'aborted':'aborted', 'preempted':'preempted'})
        
    # Create and start the instrospection server
    sis = smach_ros.IntrospectionServer('example', sm, '/SM_ROOT')
    sis.start()

    # Execute SMACH plan
    outcome = sm.execute()
    
    # Construct action server wrapper
#    asw = smach_ros.ActionServerWrapper( 'state_machine2', actionlib_tutorials.msg.AveragingAction, wrapped_container=sm, succeeded_outcomes=['outcome4'], goal_key='goal' )
#    asw.run_server()
  
    rospy.spin()
    sis.stop()

if __name__ == '__main__':
    main()
