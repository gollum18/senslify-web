# Name: verify.py
# Since: Aug. 8th, 2019
# Author: Christen Ford
# Description: Contains useful methods for verifying Senslify data objects.


def verify_reading(reading):
    """Determines if a reading is in the correct format.
    This method does not verify that keys are correct.
    
    Args:
        reading (dict): The reading to verify.
    """
    # make sure the reading type is a dictionary
    if type(reading) is not dict:
        return False

    # check that all the required fields are present
    if 'sensorid' not in reading:
        return False
    if 'groupid' not in reading:
        return False
    if 'rtypeid' not in reading:
        return False
    if 'ts' not in reading:
        return False
    if 'val' not in reading:
        return False
        
    # TODO: Check the individual data fields as well

    return True
