# Test Feature Set CAPL Functions

## ADAS

| Functions | Short Description |
| --- | --- |
| TestGetWaitADASDetectedObject | Retrieves the name of the Detected Object that triggered the wait function. |
| TestWaitForADASDetectedObjectDistance | Waits for a Detected Object for which the distance is above/below a specified value |
| TestWaitForADASDetectedObjectSpeed | Waits for a Detected Object for with a speed above/below a specified value. |
| TestWaitForADASDetectedObjectTimeToCollision | Waits for the occurrence of the first Detected Object matching the Time To Impact (TTI) conditions passed as arguments. |
| TestWaitForADASGroundTruthObjectDistance | Waits for the occurrence of the first Moving Object matching the distance conditions passed as arguments. |
| TestWaitForADASGroundTruthObjectDistance | Waits for the occurrence of the first Moving Object matching the distance conditions passed as arguments. |
| TestWaitForADASGroundTruthObjectInLane | Waits for a Moving Object which is completely in the given lane. |
| TestWaitForADASGroundTruthObjectInSameLane | Waits for a Moving Object which is completely in the lane of the ego vehicle. |
| TestWaitForADASGroundTruthObjectLaneSwitch | Waits for a Moving Object which switches lane. |
| TestWaitForADASGroundTruthObjectSpeed | Waits for the occurrence of the first Moving Object matching the speed conditions passed as arguments. |
| TestWaitForADASGroundTruthObjectTimeToCollision | Waits for the occurrence of the first Moving Object matching the Time To Collision (TTC) conditions passed as arguments. |

## AUTOSAR PDU

| Functions | Short Description |
| --- | --- |
| TestGetWaitPDUData | Calls up the content of a PDU. |
| TestGetWaitPDUsFrameData | Calls up the content of a message, packet or frame of a PDU. |
| TestJoinPDUEvent | Completes the current set of "joined events" with the transmitted event. |
| TestWaitForPDU | Waits for the occurrence of the specified PDU. |
| TestGetWaitPDUsTPIPv4DstAddr | Requests the IPv4 destination address. |
| TestGetWaitPDUsTPIPv4SrcAddr | Requests the IPv4 source address. |
| TestGetWaitPDUsTPIPv6DstAddr | Requests the IPv6 destination address. |
| TestGetWaitPDUsTPIPv6SrcAddr | Requests the IPv6 source address. |
| TestGetWaitPDUsTPTCPDstPort | Requests the TCP destination port. |
| TestGetWaitPDUsTPTCPSrcPort | Requests the TCP source port. |
| TestGetWaitPDUsTPUDPDstPort | Requests the UDP destination port. |
| TestGetWaitPDUsTPUDPSrcPort | Requests the UDP source port. |

## Collection of Event Information

| Functions | Short Description |
| --- | --- |
| testGetJoinedEventOccured | Retrieves the occurrence and the occurrence time of a joined event. |
| TestGetLastWaitElapsedTimeNS | Indicates the period of time for which the last wait function executed had to wait until being triggered. |
| TestGetLastWaitResult | Makes he last occurred return value of a TestWait instruction available. |
| TestGetStringInput | Returns the result of the last successful call of TestWaitForStringInput. |
| TestGetValueInput | Returns the result of the last successful call of TestWaitForValueInput. |
| TestGetWaitEventMsgData | Calls up the message content. |
| TestGetWaitEventSysVarData | Retrieves the system variable value that has led to the resume of a joined wait statement. |
| Ethernet Functions | Short Description |
| testGetWaitEthernetPacketData | If a Ethernet packet is the last event that triggers a wait instruction, the packet's content can be called up. |
| TestGetWaitSomeIpMessageData | If a valid SOME/IP message is the last event that triggers a wait instruction, the SOME/IP message content can be called up. |
| TestGetWaitSomeIpSDData | If a valid SOME/IP Service Discovery entry is the last event that triggers a wait instruction, the content of the SOME/IP Service Discovery entry can be called up. |
| FlexRay Functions | Short Description |
| TestGetWaitFrFrameData | If a valid FlexRay frame is the last event that triggers a wait instruction, the frame's content can be called up. |
| TestGetWaitFrFrameErrorData | If a FlexRay frame error is the last event that triggers a wait instruction, the event's content can be called up. |
| TestGetWaitFrNullFrameData | If a FlexRay Null Frame is the last event that triggers a wait instruction, the frame's content can be called up. |
| TestGetWaitFrPDUData | If a valid FlexRay PDU is the last event that triggers a wait instruction, the PDU's content can be called up. |
| TestGetWaitFrPOCStateData | If an event indicating a change of state on the FlexRay Communication Controller's protocol operation state machine is the last event that triggers a wait instruction, the event's content can be called up. |
| TestGetWaitFrStartCycleData | If a FlexRay start cycle is the last event that triggers a wait instruction, the event's content can be called up. |
| TestGetWaitFrSymbolData | If a FlexRay symbol event is the last event that triggers a wait instruction, the event's content can be called up. |
| LIN Functions | Short Description |
| TestGetWaitLinCSErrorData | Retrieves the data of a checksum error. |
| TestGetWaitLinLongDominantSignalData | If LIN LongDominantSignal is the last event that triggers a wait instruction, the frame content can be called up with this function. |
| TestGetWaitLinETFSingleResponseData | Calls up the event content. |
| TestGetWaitLinHdrData | Calls up the header content. |
| TestGetWaitLinReceiveErrData | Calls up the error content. |
| TestGetWaitLinSpikeData | If LIN Spike is the last event that triggers a wait instruction, the frame content can be called up with tis function. |
| TestGetWaitLinSyncErrorData | Retrieves the data of a synchronization error. |
| TestGetWaitLinTransmErrData | Calls up the frame content. |
| TestGetWaitLinWakeupData | |
| Scope Functions | Short Description |
| testGetWaitScopeEventData | Retrieves the data of Scope event. |
| testGetWaitScopeSignalTransitionTime | Measures the transition time of rising and falling edges of a message within the defined area. |
| testWaitForScopeAnalyseBitSegments | Starts an analysis for the defined bit segments for each bit, which is within the defined range. |
| testWaitForScopeEvent | Waits for the occurrence of Scope event. |
| testWaitForScopeFitData | The defined frame cutout is shown in the scope's graph view. (CAN) |
| testWaitForScopeFitDataFr | The defined frame cutout is shown in the scope's graph view. (FlexRay) |
| testWaitForScopeShowEdges | The defined frame cutout of the previously transition time measurement frame together with a bitmask is shown in the scope's graph view. |
| testWaitScopeGetSerialBitAnalysisData | Get specific data for a serial bit analysis. |
| testWaitScopeGetSerialBitAnalysisViolationData | If the serial bit analysis has found errors, the violations can be requested with this function. |
| testWaitScopeAnalyseSignal | Checks the bits of a message against the defined bitmask. |
| testWaitScopeExportData | Export the scope measurement. |
| testWaitScopeGetAnalysedBitSegments | Request the analysis data for a single bit. |
| testWaitScopeGetBitInfo | After a signal was analyzed, the average values of the voltages of CAN_H, CAN_L, and CAN_Diff are calculated for a defined bit range. |
| testWaitScopeGetEyeDiagramAnalysis | Used to request the analysis data for a violation found with the eye diagram analysis |
| testWaitScopeGetMaskViolation | Retrieve the data of the bitmask violations. |
| testWaitScopeGetMessageBits | Gets specific bit values from a message. |
| testWaitScopePerformEdgeAnalysis | Measures different edge parameters for falling or rising edges of a frame or node. |
| testWaitScopePerformEyeDiagramAnalysis | Used to check bits against a defined bitmask. |
| testWaitScopePerformSerialBitAnalysis | Checks the bits of a message against the defined bitmask. |
| testWaitScopePerformSignalTransitionTime | Measures the transition time of rising and falling edges of a message within the defined area on bit level. |
| testWaitScopeShowMask | The defined frame cutout together with a previously defined bitmask is shown in the scope's graph view. |
| J1939 Functions | Short Description |
| TestGetWaitJ1939PGData | If a J1939 parameter group event is the last event that triggers a wait instruction, the message content can be called up. |
| TestWaitForJ1939DTC | Waits until a defined Parameter Group and a defined Diagnostic Trouble Code (DTC) is received or a timeout occurred. |
| TestWaitForJ1939DmWithoutSPN | Waits for the occurrence of a diagnostic message with or without a defined DTC or SPN. |
| TestWaitForJ1939PG | Waits for the occurrence of the specified message aMessage. |
| A429 Functions | Short Description |
| TestWaitForA429Word | Waits for the occurrence of the valid specified A429 message. |

## Communication Concept

| Functions | Short Description |
| --- | --- |
| TestJoinChange | Join the change of a function bus value entity to the current set of waiting events. |
| TestJoinChangeCountGreater | Join the change counter of a function bus value entity reaching a given value to the current set of waiting events. |
| TestJoinChangeFlag | Join the change flag of a function bus value entity being set to the current set of waiting events. |
| TestJoinForAnswer | Join the answer to the call to the current set of waiting events. |
| TestJoinForNextCall | Join the answer to the call to the current set of waiting events. |
| TestJoinImplValue | Join the wait for a communication or distributed object impl value to the current set of waiting events. |
| TestJoinImplValueFloat | Join the wait for a communication or distributed object impl value to the current set of waiting events. |
| TestJoinImplValueInRangeFloat | Join the wait for a communication or distributed object impl value to the current set of waiting events. |
| TestJoinImplValueInRangeSInt | Join the wait for a communication or distributed object impl value to the current set of waiting events. |
| TestJoinImplValueInRangeUInt | Join the wait for a communication or distributed object impl value to the current set of waiting events. |
| TestJoinImplValueOutsideRangeFloat | Join the wait for a communication or distributed object impl value to the current set of waiting events. |
| TestJoinImplValueOutsideRangeSInt | Join the wait for a communication or distributed object impl value to the current set of waiting events. |
| TestJoinImplValueOutsideRangeUInt | Join the wait for a communication or distributed object impl value to the current set of waiting events. |
| TestJoinImplValueSInt | Join the wait for a communication or distributed object impl value to the current set of waiting events. |
| TestJoinImplValueString | Join the wait for a communication or distributed object impl value to the current set of waiting events. |
| TestJoinImplValueUInt | Join the wait for a communication or distributed object impl value to the current set of waiting events. |
| TestJoinPhysValueFloat | Join the wait for a communication or distributed object phys value to the current set of waiting events. |
| TestJoinPhysValueInRangeFloat | Join the wait for a communication or distributed object phys value to the current set of waiting events. |
| TestJoinPhysValueInRangeSInt | Join the wait for a communication or distributed object phys value to the current set of waiting events. |
| TestJoinPhysValueInRangeUInt | Join the wait for a communication or distributed object phys value to the current set of waiting events. |
| TestJoinPhysValueOutsideRangeFloat | Join the wait for a communication or distributed object phys value to the current set of waiting events. |
| TestJoinPhysValueOutsideRangeSInt | Join the wait for a communication or distributed object phys value to the current set of waiting events. |
| TestJoinPhysValueOutsideRangeUInt | Join the wait for a communication or distributed object phys value to the current set of waiting events. |
| TestJoinPhysValueSInt | Join the wait for a communication or distributed object phys value to the current set of waiting events. |
| TestJoinPhysValueUInt | Join the wait for a communication or distributed object phys value to the current set of waiting events. |
| TestJoinUpdate | Join the update of a function bus value entity to the current set of waiting events. |
| TestJoinUpdateCountGreater | Join the update counter of a function bus value entity reaching a given value to the current set of waiting events. |
| TestJoinUpdateFlag | Join the update flag of a function bus value entity being set to the current set of waiting events. |
| TestValidateImplValue | Validates a communication or distributed object value. |
| TestValidateImplValueFloat | Validates a communication or distributed object value. |
| TestValidateImplValueInRangeFloat | Validates a communication or distributed object value. |
| TestValidateImplValueInRangeSInt | Validates a communication or distributed object value. |
| TestValidateImplValueInRangeUInt | Validates a communication or distributed object value. |
| TestValidateImplValueOutsideRangeFloat | Validates a communication or distributed object value. |
| TestValidateImplValueOutsideRangeSInt | Validates a communication or distributed object value. |
| TestValidateImplValueOutsideRangeUInt | Validates a communication or distributed object value. |
| TestValidateImplValueSInt | Validates a communication or distributed object value. |
| TestValidateImplValueString | Validates a communication or distributed object value. |
| TestValidateImplValueUInt | Validates a communication or distributed object value. |
| TestValidatePhysValueFloat | Validates a communication or distributed object value. |
| TestValidatePhysValueInRangeFloat | Validates a communication or distributed object value. |
| TestValidatePhysValueInRangeSInt | Validates a communication or distributed object value. |
| TestValidatePhysValueInRangeUInt | Validates a communication or distributed object value. |
| TestValidatePhysValueOutsideRangeFloat | Validates a communication or distributed object value. |
| TestValidatePhysValueOutsideRangeSInt | Validates a communication or distributed object value. |
| TestValidatePhysValueOutsideRangeUInt | Validates a communication or distributed object value. |
| TestValidatePhysValueSInt | Validates a communication or distributed object value. |
| TestValidatePhysValueUInt | Validates a communication or distributed object value. |
| TestWaitForAnswer | Waits for the answer to a method call. |
| TestWaitForChange | Waits for the next change of a communication or distributed object value. |
| TestWaitForChangeCountGreater | Waits for changes of a communication or distributed object value. |
| TestWaitForChangeFlag | Waits for the change flag of a communication or distributed object value to be set. |
| TestWaitForImplValue | Waits for a communication or distributed object value. |
| TestWaitForImplValueFloat | Waits for a communication or distributed object value. |
| TestWaitForImplValueInRangeFloat | Waits for a communication or distributed object value. |
| TestWaitForImplValueInRangeSInt | Waits for a communication or distributed object value. |
| TestWaitForImplValueInRangeUInt | Waits for a communication or distributed object value. |
| TestWaitForImplValueOutsideRangeFloat | Waits for a communication or distributed object value. |
| TestWaitForImplValueOutsideRangeSInt | Waits for a communication or distributed object value. |
| TestWaitForImplValueOutsideRangeUInt | Waits for a communication or distributed object value. |
| TestWaitForImplValueSInt | Waits for a communication or distributed object value. |
| TestWaitForImplValueString | Waits for a communication or distributed object value. |
| TestWaitForImplValueUInt | Waits for a communication or distributed object value. |
| TestWaitForNextCall | Waits for the next call of the method to occur at the simulated provider. |
| TestWaitForPhysValueFloat | Waits for a communication or distributed object value. |
| TestWaitForPhysValueInRangeFloat | Waits for a communication or distributed object value. |
| TestWaitForPhysValueInRangeSInt | Waits for a communication or distributed object value. |
| TestWaitForPhysValueInRangeUInt | Waits for a communication or distributed object value. |
| TestWaitForPhysValueOutsideRangeFloat | Waits for a communication or distributed object value. |
| TestWaitForPhysValueOutsideRangeSInt | Waits for a communication or distributed object value. |
| TestWaitForPhysValueOutsideRangeUInt | Waits for a communication or distributed object value. |
| TestWaitForPhysValueSInt | Waits for a communication or distributed object value. |
| TestWaitForPhysValueUInt | Waits for a communication or distributed object value. |
| TestWaitForUpdate | Waits for the next update of a communication or distributed object value. |
| TestWaitForUpdateCountGreater | Waits for update of a communication or distributed object value. |
| TestWaitForUpdateFlag | Waits for the update flag of a communication or distributed object value to be set. |

## Composed Wait Points

| Functions | Short Description |
| --- | --- |
| TestJoinAnd | Completes the current set of joined events with the transmitted event.
                                    Events: auxiliary event, system variable, environment variable, message, message ID, text, signal (or system or environment variable) with value condition. |
| TestJoinAuxEvent | |
| TestJoinMessageEvent | |
| TestJoinSysVarEvent | |
| TestJoinTextEvent | |
| TestJoinOr | |
| TestJoinRawSignalMatch | |
| TestJoinSignalInRange | |
| TestJoinSignalOutsideRange | |
| TestJoinSignalMatch | |
| TestWaitForAllJoinedEvents | Waits for the current set of joined events. |
| TestWaitForAnyJoinedEvent | |
| TestWaitForJoinedEvent | Waits for the specified joined event. |
| Ethernet Functions | Short Description |
| TestJoinEthernetPacket | Completes the current set of joined events with the transmitted event. |
| TestJoinEthernetLinkStatus | Completes the current set of joined events with the transmitted event. |
| TestJoinEthernetPhyState | Completes the current set of joined events with the transmitted event. |
| TestJoinSomeIpMessage | Completes the current set of joined events with the transmitted event. |
| TestJoinSomeIpSD | Completes the current set of joined events with the transmitted event. |
| FlexRay Functions | Short Description |
| TestJoinFrFrameErrorEvent | Completes the current set of joined events with the transmitted event.
                                    Events: FlexRay frame error, FlexRay frame, FlexRay Null Frame, FlexRay PDU, change of state on the FlexRay Communication Controller's protocol operation state machine, FlexRay start cycle and FlexRay symbol. |
| TestJoinFrFrameEvent | Completes the current set of joined events with the transmitted event.
                                    Events: FlexRay frame error, FlexRay frame, FlexRay Null Frame, FlexRay PDU, change of state on the FlexRay Communication Controller's protocol operation state machine, FlexRay start cycle and FlexRay symbol. |
| TestJoinFrFrameEvent | Completes the current set of joined events with the transmitted event.
                                    Events: FlexRay frame error, FlexRay frame, FlexRay Null Frame, FlexRay PDU, change of state on the FlexRay Communication Controller's protocol operation state machine, FlexRay start cycle and FlexRay symbol. |
| TestJoinFrNullFrameEvent | Completes the current set of joined events with the transmitted event.
                                    Events: FlexRay frame error, FlexRay frame, FlexRay Null Frame, FlexRay PDU, change of state on the FlexRay Communication Controller's protocol operation state machine, FlexRay start cycle and FlexRay symbol. |
| TestJoinFrPDUEvent | Completes the current set of joined events with the transmitted event.
                                    Events: FlexRay frame error, FlexRay frame, FlexRay Null Frame, FlexRay PDU, change of state on the FlexRay Communication Controller's protocol operation state machine, FlexRay start cycle and FlexRay symbol. |
| TestJoinFrPOCState | Completes the current set of joined events with the transmitted event.
                                    Events: FlexRay frame error, FlexRay frame, FlexRay Null Frame, FlexRay PDU, change of state on the FlexRay Communication Controller's protocol operation state machine, FlexRay start cycle and FlexRay symbol. |
| TestJoinFrStartCycleEvent | Completes the current set of joined events with the transmitted event.
                                    Events: FlexRay frame error, FlexRay frame, FlexRay Null Frame, FlexRay PDU, change of state on the FlexRay Communication Controller's protocol operation state machine, FlexRay start cycle and FlexRay symbol. |
| TestJoinFrSymbolEvent | Completes the current set of joined events with the transmitted event.
                                    Events: FlexRay frame error, FlexRay frame, FlexRay Null Frame, FlexRay PDU, change of state on the FlexRay Communication Controller's protocol operation state machine, FlexRay start cycle and FlexRay symbol. |
| LIN Functions | Short Description |
| TestJoinLinCSErrorEvent | Adds an event to the set of joined events.
                                    Events: checksum error, LIN event-triggered frame single response, synchronization error |
| TestJoinLinETFSingleResponseEvent | Adds an event of type LIN Event-triggered Frame Single Response to the set of joined events. |
| TestJoinLinLongDominantSignal | Completes the current set of joined events with the transmitted event. |
| TestJoinLinSpike | Completes the current set of joined events with the transmitted event. |
| TestJoinLinSyncErrorEvent | Adds an event of type synchronization error to the set of joined events. |
| TestJoinLinHeaderEvent | Completes the current set of joined events with the transmitted event.
                                    Events: frame, frame ID (header, receive error, transmission error) |
| TestJoinLinReceiveErrorEvent | |
| TestJoinLinTransmErrorEvent | |
| TestJoinLinWakeupEvent | |
| J1939 Functions | Short Description |
| TestJoinJ1939DTCEvent | Completes the current set of joined events with the transmitted J1939 Suspect Parameter Number event. |
| TestJoinJ1939PGEvent | Completes the current set of joined events with the transmitted event. |
| A429 Functions | Short Description |
| TestJoinA429WordEvent | Completes the current set of joined events with the transmitted event. |

## Constraints and Conditions

| Functions | Short Description |
| --- | --- |
| TestAddCondition | Adds an event object or an event text as a condition. |
| TestAddConstraint | Adds an event object or an event text as a constraint. |
| TestCheckCondition | Checks whether the specified condition was already injured. |
| TestCheckConstraint | Checks whether the specified constraint was already injured. |
| TestRemoveCondition | Removes an event object or an event text that was added as a condition. |
| TestRemoveConstraint | Removes an event object or an event text that was added as a constraint. |

## Diagnostic Test Support

| Functions | Short Description |
| --- | --- |
| TestCollectDiagEcuInformation | Sends diagnostic requests to the currently selected diagnostic target and writes the responses to the report file. |
| TestJoinDiagResponseFromEcu | Adds an event to the set of joined events.
                                Events: Arrival of a diagnostic response from a specific or any ECU. |
| TestJoinDiagVariantIdentificationCompleted | Adds an event to the set of joined events that will fire when the variant identification started for the given ECU is completed. |
| TestReportWriteDiagObject | Writes the specified object in the test report as a HTML table. |
| TestReportWriteDiagResponse | Writes the received response of the request in the test report as a HTML table. |
| TestValidateDiagAuth | Initiates the diagnostics authentication process and waits until this process has completed. |
| TestValidateDiagAuthGeneric | Initiates the diagnostics authentication process and waits until this process has generic completed. |
| testWaitForDiagAuthCompleted | Initiates the diagnostics authentication process and waits until this process has completed. |
| testWaitForDiagAuthGenericCompleted | Initiates the diagnostics authentication process and waits until this process has generic completed. |
| TestWaitForDiagChangedActiveVariant | Changes the active variant for the current target. |
| TestWaitForDiagECUVariantIdentificationCompleted | Waits for the completion of the automatic variant identification algorithm. |
| TestWaitForDiagRequestSent | Waits until the previously sent request has been sent to the ECU. |
| TestWaitForDiagResponse | Waits for arrival of the response to the given request. |
| TestWaitForDiagResponseStart | Waits for the arrival of the response to a sent request. |
| TestWaitForDiagSetIdentifiedVariant | Performs a variant identification and activates the found variant. |
| TestWaitForDiagVariantIdentificationCompleted | Waits for the completion of the automatic variant identification algorithm. |
| TestWaitForDoIPActivationLineStartup | Waits until DoIP Activation Line start-up time has passed. |
| TestWaitForGenerateKeyFromSeed | Generates the security key from the seed using the configured Seed and Key DLL. |
| TestWaitForUnlockEcu | Tries to unlock an ECU. |
| TestWaitForDiagSecurityTaskCompleted | Initiates the diagnostics generic security task and waits until this task has completed. |

## Fault Injection Functions

| Functions | Short Description |
| --- | --- |
| TestDisableMsg | Prevents all sending of the message except the sending by calling the function testSetMsgEvent. |
| TestDisableMsgAllTx | Prevents all sendings of tx messages of the node except the sending with testSetMsgEvent. |
| TestEnableMsg | Enables the sending of the message. |
| TestEnableMsgAllTx | Enables the sending of all tx messages of a node. |
| testILSetMessageProperty | Sets the internal property of a message, assigned to the node. |
| testILSetNodeProperty | Changes an internal property of the specified node. |
| TestResetAllFaultInjections | Reset all fault injection settings. |
| TestResetMsgCycleTime | Resets the cycle time of the message to the database cycle time. |
| TestResetMsgDlc | Resets the Dlc of the message to the Dlc of the database. |
| TestSetMsgCycleTime | Assigns a new cycle time to the message. |
| TestSetMsgDlc | Assigns a new DLC to the message. |
| TestSetMsgEvent | Sends the message once. |

## OEM Add-on Based Fault Injection Functions

|  | Note
                                        These functions are not available for all OEM add-ons, the availability depends on the CANoe Interaction Layer. |
| --- | --- |

| Functions | Short Description |
| --- | --- |
| TestDisableCRCCalculation | Disables the CRC calculation of a message. |
| TestDisableMsgSequenceCounter | Disables the message sequence counter. |
| TestDisableUpdateBit | Disables the standard behavior of the update bit and sets the value of the update bit to a constant value. |
| TestEnableCRCCalculation | Enables the CRC calculation of a message. |
| TestEnableMsgSequenceCounter | Enables the message sequence counter. |
| TestEnableUpdateBit | Enables the standard behavior of the update bit. |
| TestFRILCalculateChecksum | Calculates the corresponding CRC checksum based on the payload. |
| TestFRILEnableTimingCyclic | Controls the cyclic timing of PDUs. The cyclic timing can be enabled/ disabled. |
| TestFRILEnableTimingEvtTrg | Controls the event triggered timing of PDUs. The event triggered timing can be enabled/ disabled. |
| TestFRILEnableTimingImmed | Controls the immediate timing of PDUs. The immediate timing can be enabled/ disabled. |

## Parallel Functions

| Functions | Short Description |
| --- | --- |
| testStartParallel | Starts a parallel test execution. |
| testWaitForParallel | Waits for a specific parallel test execution. |
| testWaitForAllParallel | Waits for all current parallel test executions. |

## Signaling of User-defined Events

| Functions | Short Description |
| --- | --- |
| TestSupplyTextEvent | Signals the specified event. |

## Signal Based Tests

| Functions | Short Description |
| --- | --- |
| checkSignalInRange | Checks the value of the signal, the system variable or the environment variable against a condition. |
| testValidateSignalInRange | |
| testValidateSignalOutsideRange | |
| CheckSignalMatch | Checks a given value against the value of the signal, the system variable or the environment variable. |
| TestValidateSignalMatch | Checks a given value against the value of the signal, the system variable or the environment variable. |
| GetRawSignal | Retrieves the current raw value of a signal. |
| getSignal | Gets the value of a signal. |
| getSignalTime | Gets the time point when the signal value has been changed to the current value. |
| RegisterSignalDriver | Registers the given callback as a 'signal driver' for the signal. |
| SetRawSignal | Sets the raw value of a signal. |
| SetSignal | Sets the transmitted signal to the accompanying value. |
| TestResetEnvVarValue | Resets an environment variable to initial value. |
| TestResetNamespaceDistObjValues | Resets all distributed objects member values of the given namespace (and all sub-namespaces) to their initial value.. |
| TestResetNamespaceSysVarValues | Resets all system variables of the given namespace (and all sub-namespaces) to their initial value. |
| TestResetNodeSignalValues | Resets all tx-signals of a node to their initial value. |
| TestResetSignalValue | Resets a signal to initial value. |
| TestResetSysVarValue | Resets a system variable to initial value. |

## Symbol Recording

| Functions | Short Description |
| --- | --- |
| TestReportAddToRecordingGroup | Adds a symbol to the recording group in the test report. |
| TestReportCreateRecordingGroup | Creates a recording group in the test report. |
| TestReportStartRecording | Starts the recording of a symbol in the test report. |
| TestReportStartRecordingGroup | Starts the recording of the recording group in the test report. |
| TestReportStopAllRecordings | Stops all recordings in the test report. |
| TestReportStopRecording | Stops the recording of the symbol in the test report. |
| TestReportStopRecordingGroup | Stops the recording of the recording group in the test report. |

## Test Controlling

| Functions | Short Description |
| --- | --- |
| TestSetEcuOffline | Disconnects the ECU from the bus. |
| TestSetEcuOnline | Connects the ECU to the bus. |
| testStartParallel | Starts parallel execution of the specified function. |

## Test Execution

| Functions | Short Description |
| --- | --- |
| TestGetTestExecutionVerdict | Gets the verdict of a finished test execution. |
| TestStartTestExecution | Starts the test execution. |
| TestStopTestExecution | Stops the test execution. |
| TestWaitForTestExecutionFinished | Waits until the test execution is finished. |

## Test Feature Set for K-Line

| Functions | Short Description |
| --- | --- |
| TestGetWaitEventKLineByte | If a byte is the last event that triggers a wait instruction, the content can be called up with this function. |
| TestGetWaitEventKLineFrame | If a K-Line frame is the last event that triggers a wait instruction, the content can be called up with this function. |
| TestWaitForDiagChannelClosed | Waits for the occurrence of the state change of a diagnostic channel to the state Closed. |
| TestWaitForDiagChannelConnected | Waits for the occurrence of the state change of a diagnostic channel to the state Connected. |
| TestWaitForDiagKLineByteReceived | Waits for the occurrence of a received byte. |
| TestWaitForDiagKLineByteTransmitted | Waits for the occurrence of a transmitted byte. |
| TestWaitForDiagKLineFrameReceived | Waits for the occurrence of a received valid message. |
| TestWaitForDiagKLineFrameTransmitted | Waits for the occurrence of a transmitted valid message. |

## Test Report

| Functions | Short Description |
| --- | --- |
| TestCaseComment | Within a test case a commentary can be taken over into the report. |
| testGetCurrentTestCaseID | Returns the ID of the current test case. |
| testGetCurrentTestCaseTitle | Returns the name of the current test case. |
| testGetTestConfigurationName | Returns the name of the test configuration. |
| testGetTestUnitName | Returns the name of the test unit. |
| TestReportAddEngineerInfo | Information pairs of name and description can be taken up into the report in the areas TestEngineer, TestSetUp, and device (SUT). |
| TestReportAddSetupInfo | |
| TestReportAddSUTInfo | |
| TestReportAddExtendedInfo | Takes over information into the protocol that is not subject to processing by aCANoe DE product. |
| TestReportAddExternalRef | Adds an external reference to the report. |
| TestReportAddImage | Takes over the reference to a file that contains an image into the protocol. |
| TestReportAddMiscInfo | Information pairs of name and description can be taken up into an additional information area in the report. |
| TestReportAddMiscInfoBlock | Generates a new information block for additional information pairs in the report. |
| TestReportAddWindowCapture | Creates a screen capture of a Graphics, Statistics, Data or Trace Window. |
| TestReportFileName | Sets the name of the report file using the user interface. |
| TestReportWriteDiagObject | Writes the specified object in the test report as a HTML table. |
| TestReportWriteDiagResponse | Writes the received response of the request in the test report as a HTML table. |

## Test Status

| Functions | Short Description |
| --- | --- |
| testGetCurrentCycle | Returns the current cycle of the test. |
| TestAcquireStatusLED | Assigns the test module state to an LED (standalone mode). |

## Test Structuring

|  | Note
                                        The user can display structured data in the test report. The data is formatted as a table that can contain multiple rows and columns.
                                        A header row can be specified by the function TestInfoHeadingBegin and TestInfoHeadingEnd. Other table rows can be specified by the function TestInfoRow. A row and a header row can be divided into multiple columns using the function TestInfoCell.
                                        The content of the table will be displayed using one of the test step functions: TestStep, TestStepPass, TestStepFail, TestStepWarning. |
| --- | --- |

| Functions | Short Description |
| --- | --- |
| TestCaseDescription | Writes a description text for a test case into the report. |
| TestCaseSkipped | Marks a test case as unexecuted. |
| TestCaseTitle | The title of a test case is acquired automatically from the test case name in the CAPL program. |
| testCasePrecondition | Sets a precondition to be fulfilled. |
| TestCaseReportMeasuredValue | Adds a report entry in the measured values table. |
| TestFunctionTitle | Sets the title of the current test function. |
| TestGroupBegin | Opens a test group. |
| TestGroupEnd | Closes a test group. |
| TestInfoTable | Creates a new table to display structured data in the test report. |
| TestInfoHeadingBegin | Starts a header row into a table. |
| TestInfoHeadingEnd | Ends a header row. |
| TestInfoRow | Starts a row in a table. |
| TestInfoCell | Adds a cell to a previous row or header row. |
| TestModuleDescription | Writes a description text for the test module into the report. |
| TestModuleTitle | The title of the test module is acquired automatically from the name of the test node in the simulation structure. |
| testSequencePrecondition | Sets a precondition to be fulfilled. |
| TestSequenceTitle | Sets the title of the current test sequence. |
| TestStep | Reports a test step without influence on the result. |
| TestStep, TestStepPass, TestStepFail, TestStepWarning, TestStepInconclusive, TestStepErrorInTestSystem | Describes a test step that causes an error in test system. |
| TestStepFail | Describes a test step that causes an error. |
| TestStep, TestStepPass, TestStepFail, TestStepWarning, TestStepInconclusive, TestStepErrorInTestSystem | Describes a test step which can not clearly marked as passed or failed . |
| TestStepPass | Reports a test step that was executed as expected. |
| TestStepWarning | Describes a test case that was executed without errors but whose result could contribute to a problem later on. |

## Verdict Interaction

| Functions | Short Description |
| --- | --- |
| TestCaseFail | Sets the verdict of the current test case to fail. |
| TestGetVerdictLastTestCase | Returns the verdict of the last elapsed or current test case. |
| TestGetVerdictModule | Returns the current verdict out of the test module. |
| TestSetVerdictModule | Sets the verdict of the test module. |
| TestStepFail | Describes a test step that causes an error. |

## [VT System]

| Functions | Short Description |
| --- | --- |
| TestWaitForVTSStateRestore | restores the default or start state of VT System channels. |

## Wait Instructions

| Functions | Short Description |
| --- | --- |
| TestAddRange | Adds a new range that is allowed for dialog input. |
| TestAddTriggerTesterAction | Creates a trigger for a tester action. |
| TestAddValueTableEntry | Adds a new value table entry. |
| TestCreateInputRange | Creates an input dialog. |
| TestCreateInputTable | Creates a selection dialog. |
| TestCreateTesterAction | Creates a tester action. |
| TestGetByteInput | After a dialog with byte input is closed you can use this function to get the input. |
| testIsAsynchronousCheckEvaluationEnabled | Return true if asynchronous evaluation of background checks is enabled. |
| TestValidateSystemCall | Starts an external application and reports the result. |
| TestValidateSystemCallWithExitCode | Starts an external application and checks its exit code. The result is reported. |
| TestValidateTesterAction | Creates a popup window with given tester instruction. |
| TestValidateTesterConfirmation | Creates a popup window that presents the given string to the tester. The result is reported. |
| testWaitForAllParallel | Waits until execution of all parallel threads finished. |
| TestWaitForAuxEvent | Waits for the signaling of the specified auxiliary event from a connected NodeLayer module. |
| TestWaitForByteInput | Opens a dialog for byte array input. |
| testWaitForCheckQuery | Request status data from the asynchronous evaluation for a specific check. |
| testWaitForHILAPISignalGeneratorFinished | Waits until a running generator has finished. |
| testWaitForHILAPISignalGeneratorLoaded | Waits until a signal generator is fully loaded and ready to start. |
| TestWaitForInput | After you have created a value table or range dialog use this function to open the dialog. |
| TestWaitForMeasurementEnd | Waits for the end of the measurement. |
| TestWaitForMessageBox | Creates a popup window that presents the given string to the tester. |
| testWaitForParallel | Waits until execution of the specified thread has finished. |
| TestWaitForReplay | Starts playing the replay file and waits until the execution has been finished. |
| TestWaitForRawSignalMatch | Checks the given raw value against the value of the signal. The resolution of the signal is considered. |
| TestWaitForSignalChange | Waits for an event from a signal which value is changed. |
| TestWaitForSignalInRange | Checks if the signal, the system or the environment variable value is within or outside a defined value range. |
| TestWaitForSignalOutsideRange | |
| TestWaitForSignalMatch | Checks if a given value matches the value of the signal, the system variable or the environment variable. |
| TestWaitForSignalUpdate | Waits for an event from a signal. |
| TestWaitForSysVar | Waits for the next system variable. |
| TestWaitForStringInput | Creates a dialog in which the tester can enter a text. |
| TestWaitForSyscall | Starts an external application and check its exit code. |
| TestWaitForTesterConfirmation | Creates a popup window and waits for tester confirmation. |
| TestWaitForTextEvent | Waits for the signaling of the specified textual event from the individual test module. |
| TestWaitForTimeout | Waits until the expiration of the specified timeout time. |
| TestWaitForTimeoutSilent | Waits until the expiration of the specified timeout time. The function does not write in the Test Feature Set report. |
| testWaitForValueChangePropagation | Wait until values (SVs, VEs) are propagated to the asynchronous evaluation. |
| TestWaitForUserFileSync | Starts synchronization of user files between client and server system in a distributed environment. |
| TestWaitForValueInput | Creates a dialog in which the tester can enter a number. |
| CAN Functions | Short Description |
| TestWaitForBusIntegration | Waits for Bus Integration of a specified CAN channel. |
| TestWaitForMessage | Waits for the occurrence of a specified message. |
| TestWaitForSignalAvailable | Tests the availability of a specific signal and waits if necessary until its availability. |
| TestWaitForSignalsAvailable | Tests the availability of all the send signals of a node and waits if necessary until all the send signals of the node are available. |
| Ethernet Functions | Short Description |
| TestWaitForEthernetLinkStatus | Waits for an Ethernet link status. |
| TestWaitForEthernetPacket | Waits for the occurrence of the first Ethernet packet matching the conditions passed as arguments. |
| TestWaitForEthernetPhyState | Waits for the occurrence of the specified Ethernet PHY state. |
| TestWaitForSomeIpMessage | Waits for the next SOME/IP message to occur that meets the conditions passed as arguments. |
| TestWaitForSomeIpSD | Waits for the next SOME/IP Service Discovery entry to occur that meets the conditions passed as arguments. |
| FlexRay Functions | Short Description |
| TestWaitForFrFrame | Waits for the occurrence of the valid specified FlexRay frame. |
| TestWaitForFrFrameError | Waits for the occurrence of FlexRay frame error event. |
| TestWaitForFrNullFrame | Waits for the occurrence of the specified FlexRay Null Frame. |
| TestWaitForFrPDU | Waits for the occurrence of the valid specified FlexRay PDU event. |
| TestWaitForFrPOCState | Waits for the occurrence of change of state on the FlexRay Communication Controller's protocol operation state machine. |
| TestWaitForFrStartCycle | Waits for the occurrence of the specified FlexRay start cycle event. |
| TestWaitForFrSymbol | Waits for the occurrence of a FlexRay symbol on the bus. |
| TestWaitForSignalAvailable | Tests the availability of a specific signal and waits if necessary until its availability. |
| TestWaitForSignalsAvailable | Tests the availability of all the send signals of a node and waits if necessary until all the send signals of the node are available. |
| LIN Functions | Short Description |
| TestWaitForLinBitStreamStatus | Waits until the sending of a LIN bitstream is started or stopped. |
| TestWaitForLinCSError | Waits for a checksum error for the specified amount of time. |
| TestWaitForLinETFSingleResponse | Waits for the occurrence of a LIN Event-triggered frame with a single response for the specified associated frame. |
| TestWaitForLinHeader | Waits for the Header occurrence of the specified LIN frame. |
| TestWaitForLinLongDominantSignal | Waits for the occurrence of a LIN long dominant signal. |
| TestWaitForLinReceiveError | Waits for the occurrence of LIN Receive Error event. |
| TestWaitForLinScheduleChange | Waits until the LIN scheduler reaches the specified table and slot index. |
| TestWaitForLinSpike | Waits for the occurrence of a LIN Spike event. |
| TestWaitForLinTransmError | Waits for the occurrence of LIN Transmission Error event. |
| TestWaitForLinWakeupFrame | Waits for the occurrence of LIN Wakeup frame. |
| TestWaitForMessage | Waits for the occurrence of a specified message. |
| TestWaitForSignalAvailable | Tests the availability of a specific signal and waits if necessary until its availability. |
| TestWaitForSignalsAvailable | Tests the availability of all the send signals of a node and waits if necessary until all the send signals of the node are available. |
| Scope Functions | Short Description |
| testWaitForScopeEvent | Waits for the occurrence of Scope event. |
| J1939 Functions | Short Description |
| TestWaitForJ1939DTC | Waits until a defined parameter group and a defined Suspect Parameter Number (SPN) is received or a timeout occurred. |
| TestWaitForJ1939PG | Waits for the occurrence of the specified message. |
