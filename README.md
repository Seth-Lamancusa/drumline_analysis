# drumline-analysis

Simple script for analyzing a recording of marching snare music. Appropriate for music without flams or buzzes. Useful for detecting and quantifying volume consistency, second diddle strength, diddle spacing, and general rhythmic accuracy. To use, change INTENDED_BPM and INTENDED_RHYTHM, ensure MAKE_NEW_RECORDING and SECONDS are set appropriately, and run the script. It will record your audio, indicated by a terminal prompt, and a .wav file will be generated and analyzed. You'll recieve a friendly matplotlib chart with insights into your rhythmic accuracy and volume. After generating the plot once, set OMIT_PEAKS to remove any false positives (if you don't, the error detection will NOT work correctly). Then, regenerate your plot with MAKE_NEW_RECORDING set to False. As for the plot you get, the blue hashes indicate the mathematically perfect rhythm while the red indicate what you played. Stats are present related to your error.
