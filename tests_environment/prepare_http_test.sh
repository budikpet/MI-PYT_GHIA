#!/bin/bash 
# Requires GITHUB_USER environment var

FILE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PARENT_DIR="$(dirname "$FILE_DIR")"
HTTP_TESTS_FIXTURES="$PARENT_DIR""/test/test_unit/fixtures"
TEST_CONFIG_NAME="test_config"
TEST_CONFIG_FILE=$HTTP_TESTS_FIXTURES"/"$TEST_CONFIG_NAME".cfg"

echo $HTTP_TESTS_FIXTURES

if [ -f $TEST_CONFIG_FILE ]
then
    NEW_NAME=$TEST_CONFIG_NAME"_ORIGINAL.cfg"
    echo "Creating copy of the existing "$TEST_CONFIG_NAME".cfg as "$NEW_NAME
    echo "Renaming cassettes folder."

    cp $TEST_CONFIG_FILE $HTTP_TESTS_FIXTURES"/"$NEW_NAME
    mv $HTTP_TESTS_FIXTURES"/cassettes" $HTTP_TESTS_FIXTURES"/cassettes_ORIGINAL"
fi

echo "Creating current config file."
echo "[github]" > $TEST_CONFIG_FILE
echo "base=https://api.github.com" >> $TEST_CONFIG_FILE
echo "reposlug=mi-pyt-ghia/"$GITHUB_USER >> $TEST_CONFIG_FILE