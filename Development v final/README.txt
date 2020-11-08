Instructions to use the smart programming program

There are five main files:

-) Launcher
-) SmartProgrammingAnalyzer
-) final_oxram_prog_v3_6
-) madClassesAndFunctions_v3
-) variables_testParams_v3

Only the file Launcher has to be called. The test plans have to be written in the excel file SmartProgrammingTestFlow.xls

-) The first sheet ("TestFlow") will contain the all the parameters of the smart programming operations to do.
-) The "MainParameters" sheet contains the parameters of the test, like lot number, die number, etc. They will be used to create a specific folder. If the Electroglass interface is used, the parameters are given by that software, and not by this sheet.
-) The "DefaultStrategies" sheet only contains the default values that will be given to the operations in case some of them are missing from sheet "TestFlow". They could be changed or not, but it's not something crucial.

The parameters to be filled in the "TestFlow" are:

-) Test -> the number of the test. This number IS NOT the number of the test file that is created - it's only for personal reference. A number must be COMPULSORILY entered. If a number is not in the row, the test plan will not be done. This is due that the program starts executing the plans only if it detects a number in this column.
-) Plan -> the test plan to be made. Only for operations are allowed: "read", "set", "reset", or "forming". They must be in small letters and separated from each other only with a comma, no space. The kind of read that will be used (the range) is given in the sheet "MainParameters". There are some rules on how to fill this, see errors below.
-) Rep Plan -> the number of times that the plan will be repeated. This is not related at all to any smart programming. The plan given before will simply be repeated, indepenedently of if it is a smart programming or not (for example for cycling). If no number is given the default is used (0 repetitions).
-) Strategy -> the smart programming strategy. Only "V" for voltage increase, "SR" for Set-Reset (Switch-Back), and "TB" for TwinBit, are valid. If something else is introduced, no strategy will be applied.
-) Vs -> bitline voltage. Necessary to have a number if SET or FORMING are applied. Not necessary for RESET.
-) Vr -> sourceline voltage. Necessary to have a number if RESET is applied. Not necessary for SET or FORMING.
-) Rep Set -> number of repetitions of a SET. If a smart programming strategy is used, this field gives the number of times that it is repeated ONLY TO THE CELLS THAT DIDN'T SWITCH. For V, each repetition will be with an increased voltage (given in another field). For SR and TB, the repetition applies exactly the same operation.
-) Rep Reset -> number of repetitions of RESET. Same as before, but for RESET.
-) Rep Forming -> number of repetitions of FORMING. Same as before, but for FORMING.
-) ts -> programming time of the bitline. The programming time of the pulse in the bitline, only necessary for SET and FORMING and given in microseconds.
-) tr -> programming time of the sourceline. The programming time of the pulse in the bitline, only necessary for RESET and given in microseconds.
-) Vgs -> gate voltage when a pulse in the bitline is applied. Only necessary for SET or FORMING.
-) Vgs -> gate voltage when a pulse in the bitline is applied. Only necessary for RESET.
-) Step Vs -> the step increased during the V operation in the bitline voltage. Only used when the strategy is V and when SET or FORMING are used.
-) Step Vr -> the step increased during the V operation in the sourceline voltage. Only used when the strategy is V and when RESET is used.
-) Ron -> SET threshold voltage.
-) Roff -> RESET threshold voltage.
-) Rform -> FORMING threshold voltage.
-) Vsmart -> voltage of the SwitchBack strategy. Only used when SR strategy is selected. If a SwitchBack RESET is applied, Vsmart is the voltage of SET when it's reprogrammed. If a SwitchBack SET is applied, Vsmart is the voltage of RESET when it's reprogrammed. The programming time is the one given by ts and tr, respectively.
-) Dies -> used to select in which dies the testplans will be applied. When you are using the interface to move through several dies, you might want to do different operations in each one. In one of the testplans wants to be done on a single die, it must be written in this field in the format "X;Y", that is, the coordinates separated by a semicolon. The program will check if the current die corresponds to that one and if it is, it will apply the test plan. If you want to make a test plan to every single die (for example, a forming), you have to write any other thing in that field that doesn't have the format "X;Y", or simply leave it blank. In that case, the program will apply that test plan to every die.


The Launcher file checks both for errors and warnings in the "TestFlow" sheet. 

-) Errors are important missing or wrong parameters in the "TestFlow" sheet that could cause a problem in the midle of the execution of the program. If errors are found, the program is stopped before starting. 
-) Warnings are some missing or wrong parameters that are not absolutely crucial for the good execution of the program. Warnings are written down but the program is not stopped. The missing or wrong parameters are changed by some default value.

Possible errors:

1) Having a read operation in a position different that the beginning. Each operation (set, reset or forming) is accompanied ALWAYS by a read afterwards. Therefore, you should not add a read in the test plan, unless it is only at the beginning (to check the initial state of the cell). If a read is added at the beginning, the plan cannot be repeated or it would also cause a double read in between. RepPlan > 0 and read operation at the beginning are not compatible and an error will be raised.
2) Forming operation can only be added once in the test plan (it doesn't make sense to form more than once). If a smart forming operation wants to be done, strategy V needs to be used.
3) Forming operation cannot be accompanied by a set or a reset, in order to separate the two kinds of operations better. 
4) If one of the three resistance thresholds is 0 or not a number, an error is raised.
5) The strategy is invalid. At this moment, an error will be raised only if forming operation is accompanied by SR or TB.
6) The voltage is invalid. For example, if you are doing a SET operation, the Vs voltage has to be a number. If it's a RESET, the Vr voltage should be a number. Same thing for Vgs and Vgr. However, if we're doing a SET and Vr is not a number, only a warning is raised, but the program is not stopped since Vr is only used for RESET.
7) The same as before but with time.