@echo off

rem Set the option for input file
set option1=-i

rem Set the input file path
set input_file_path=D:\build2auto\bos-tools\bos-onboarding\test\darshan_test_cb.xlsx

rem Set the output directory
set output_dir=jineshtest

rem Set the option for output
set option2=-o

rem Run the first Python script
"D:\build2auto\bos-tools\bos-onboarding\b2auto\Scripts\python.exe" "D:\build2auto\bos-tools\bos-onboarding\sheet2udmi.py" %option1% "%input_file_path%" %option2% "%output_dir%"

rem Run the second Python script
"D:\build2auto\bos-tools\bos-onboarding\b2auto\Scripts\python.exe" "D:\build2auto\bos-tools\bos-onboarding\sheet2config.py" %option1% "%input_file_path%" %option2% "%output_dir%"

pause