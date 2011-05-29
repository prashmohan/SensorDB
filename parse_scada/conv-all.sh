for file_name in `find UCProject_UCB_SODAHALL -name "*.DAT"`; do
    ./a.out < $file_name > $file_name.csv
done
