#!/usr/bin/env python

# Extract Observation and action per trial for aac task
# For Ryan's computation
# This is modified script to AAC data from Texas A&M

import csv
import pandas as pd
import numpy as np
import sys,os


def getCondition(row):
    """
    Return Condition of the Trial

    Condition Mapping:
    1 : Avoid-Threat
    2 : Approach-Reward
    3 : Conflict: 2 Point
    4 : Conflict: 4-Point
    5 : Conflict: 6-Point

    Parameter
    _________
    trial_type str
        5 digit of the Trial Type
    """
   
    pts_other = row['PtsOther']
    outcome_pts = row['OutcomePts (Pts received)']
    positive = row['Piname (name of positive image file)']
    negative = row['Niname (name of negative image file)']

    if ('PI' in positive) and ('PI' in negative): 
        return 2
    if ((pts_other + outcome_pts) == 0):
        return 1

    if (pts_other + outcome_pts) == 2:
        return 3
    if (pts_other + outcome_pts) == 4:
        return 4
    if (pts_other + outcome_pts) == 6:
        return 5

    # Should never receive 0
    return 0

def isFlip(row):
    """
    Returns to True if the position numbering needs to be flip

    Avatar Position Number referse to the side where
    Higher Number end refers to the side with reward.
    If reward is 0 than, it's the side with the Positive Image

    True Case: (9 on the Left)
     9   8   7   6  5   4   3   2   1
    -|---|---|---|--|---|---|---|---|
    -4  -3  -2  -1  0   1   2   3   4  // Task Position Mapping

    False Case: ( 9 on the right)
     1   2   3   4  5   6   7   8   9
    -|---|---|---|--|---|---|---|---|
    -4  -3  -2  -1  0   1   2   3   4  // Task Position Mapping

    Parameter
    _________
    trial_type str
        5 digit of the Trial Type e.g 10400
    """
    ptsother = row['PtsOther']
    outcomepts = row['OutcomePts (Pts received)']

    neg_image_side = row['Negative Image Side (1=L and 0=R)']
    positive = row['Piname (name of positive image file)']
    negative = row['Niname (name of negative image file)']

    endPos = row['EndPos (end position of the avatar)']

    # Avoid-Threat Condition
    # Approach Reward Condition since neigther outcome and neither pts other have points
    if (ptsother + outcomepts) == 0:
        if neg_image_side == 'L': 
            # Side with the positive image is a 9
            return False
        else: 
            return True

    # Approach-Reward trials
    # Points side should always on the right (9)
    if 'PI' in positive and 'PI' in negative:
        if ( (neg_image_side == 'L') and (ptsother > 0) ):
            # This means, Right side has the points, so right side shoule be 9.
            return False
        if ( (neg_image_side == 'L') and (ptsother == 0) ):
            # This means, Left side has the points, so Left side shoule be 9.
            return True

        if ( (neg_image_side == 'R') and (ptsother > 0) ):
            # This means, Left side has the points, so right should be 1
            return True

        if ( (neg_image_side == 'R') and (ptsother == 0) ):
            # This means, Left side has the points, so right should be 1
            return True


    # If it gets to here, it means, it must be conflict trials
    # Regular Trial with one side + and other side -
    # So Follow the rules based on where the neg image is.
    if 'NI' in negative:
        if ( neg_image_side == 'L'):
            # Negative Image is on the left, so 9 should be on the left
            return True
        if (neg_image_side == 'R'):
            # Negative image ins on the right, so 9 should be on the right
            return False



    # Default is True
    return True

def returnFirstPosition(row):
    """Returns the first task position mapping. Accounts for negative"""
    startingPosition = row['StartPos (starting position of the avatar)']
    return startingPosition

def getFinalPosition(row):
    """
    Return final position mapping
    """
    finalPos = row['EndPos (end position of the avatar)']

    positions = [1,2,3,4,5,6,7,8,9]

    # Flipt the positions based on trial_type
    if isFlip(row):
        positions.reverse()

    # Mapping the Task Position with new mapping
    positionMap = {}
    positionMap[-4.0] = positions[0]
    positionMap[-3.0] = positions[1]
    positionMap[-2.0] = positions[2]
    positionMap[-1.0] = positions[3]
    positionMap[0.0] = positions[4]
    positionMap[1.0] = positions[5]
    positionMap[2.0] = positions[6]
    positionMap[3.0] = positions[7]
    positionMap[4.0] = positions[8]

    return positionMap[finalPos]


def getFirstPosition(row):
    """
    Return First position mapping
    """
    startingPosition = returnFirstPosition(row)

    positions = [1,2,3,4,5,6,7,8,9]

    # Flipt the positions based on row
    if isFlip(row):
        positions.reverse()

    # Mapping the Task Position with new mapping
    positionMap = {}
    positionMap[-4.0] = positions[0]
    positionMap[-3.0] = positions[1]
    positionMap[-2.0] = positions[2]
    positionMap[-1.0] = positions[3]
    positionMap[0.0] = positions[4]
    positionMap[1.0] = positions[5]
    positionMap[2.0] = positions[6]
    positionMap[3.0] = positions[7]
    positionMap[4.0] = positions[8]

    return positionMap[startingPosition]


def getObservation1FinalPosition(row):
    """
    Returns the finalposition mapping for observation 1

    2 = negative image
    3 = positive image
    4 = positive image +2
    5 = negative image +2
    6 = negative image +4
    7 = negative image +6

    trial_type: str
        5 digit trial type
    responses: Array()
        Array of responses, -1: left, 1: right
    """
    leftValence = int(trial_type[0])
    rightValence = int(trial_type[1])
    leftReward = int(trial_type[2])
    rightReward = int(trial_type[3])
    startingPosition = returnFirstPosition(trial_type)

    finalStep = startingPosition
    try:
        for step in range(0,len(responses)):
            finalStep = finalStep + responses[step]
    except ValueError:
        # Didn't click so last position is intial position
        pass

    # finalStep is the task position mapping

    # When finalStep is on the Left side
    if finalStep < 0 and leftValence == 1.0 and leftReward == 0: # Negative Image side and No Reward
        return 2
    if finalStep < 0 and leftValence == 0.0 and leftReward == 0: # Positive Image side and No Reward
        return 3
    if finalStep < 0 and leftValence == 0.0 and leftReward == 2: # Positive Image side with +2 Reward
        return 4
    if finalStep < 0 and leftValence == 1.0 and leftReward == 2: # Negative Image side with +2 Reward
        return 5
    if finalStep < 0 and leftValence == 1.0 and leftReward == 4: # Negative Image side with +4 Reward
        return 6
    if finalStep < 0 and leftValence == 1.0 and leftReward == 6: # Negative Image side with +6 Reward
        return 7

    # When finalStep is on the Right side or Middle
    if finalStep >= 0 and rightValence == 1.0 and rightReward == 0: # Negative Image side with No Reward
        return 2
    if finalStep >= 0 and rightValence == 0.0 and rightReward == 0: # Positive Image side with No Reward
        return 3
    if finalStep >= 0 and rightValence == 0.0 and rightReward == 2: # Positive Image side with +2 Reward
        return 4
    if finalStep >= 0 and rightValence == 1.0 and rightReward == 2: # Negative Image side with +2 Reward
        return 5
    if finalStep >= 0 and rightValence == 1.0 and rightReward == 4: # Negative Image side with +4 Reward
        return 6
    if finalStep >= 0 and rightValence == 1.0 and rightReward == 6: # Negative Image side with +6 Reward
        return 7


def getOutcome(row):
    """
    2 = negative image
    3 = positive image
    4 = positive image +2
    5 = negative image +2
    6 = negative image +4
    7 = negative image +6

    #  Task Outcome:
    8 : Negative Outcome
    9 : Positive Outcome
    """
    image_shown = row['OutcomeImage (image shown)']
    outcome_points = row['OutcomePts (Pts received)']

    if 'NI' in image_shown: outcome = 8
    if 'PI' in image_shown: outcome = 9
    if outcome == 8 and outcome_points == 0: # Negative Image and No Reward
        return 2
    if outcome == 9 and outcome_points == 0: # Positive Image and No Reward
        return 3
    if outcome == 9 and outcome_points == 6: # Positive Image and +6 Points # Don't actually gain the +6 points
        return 3
    if outcome == 9 and outcome_points == 4: # Positive Image and +4 Points # Don't actually gain the +4 points
        return 3
    if outcome == 9 and outcome_points == 2: # Positive Image and +2 Points
        return 4
    if outcome == 8 and outcome_points == 2: # Negative Image and +2 Points
        return 5
    if outcome == 8 and outcome_points == 4: # Negative Image and +4 Points
        return 6
    if outcome == 8 and outcome_points == 6: # Negative Image and +6 Points
        return 7



def flipSign(float_num):
    """Flip the sign of a given float"""
    if float_num >= 0:
        return -float_num
    else:
        return abs(float_num)

def getObservation1(row):
    """
    Return sequence for Observation 1.
    All ones for each move until final position

    """
    firstPosition = row['StartPos (starting position of the avatar)']
    finalsequence = []
    finalsequence.append(1) # o1_0 needs to awlways be 1

    mappedOutcome = getOutcome(row)

    finalsequence.append(mappedOutcome)

    return finalsequence


def getObservation2(row):
    """
    Return Data for Observation 2 which is conidition repeated 9 times
    """
    return [ getCondition(row) for x in range(0,2)]


def getObservation3(row):
    """
    Return Data sequency for Observation 3 which is the position number and final position summation
    """
    firstPosMap = getFirstPosition(row)
    lastPosMap = getFinalPosition(row)
    sequence = []

    finalStep = firstPosMap

    sequence.append(1) # Add the first PosMap before adding the rest
    sequence.append(lastPosMap + 1) # Since 2 = 1, 3 = 2, 4 = 3, etc

    return sequence



def getLeftRightMap(trial_type,response):
    """
    Return Action Mapping, 1 or 2

    Action Mapping:
    1 = Left
    2 = Right
    """
    if isFlip(trial_type) and response == -1.0:
        return 2
    if isFlip(trial_type) and response == 1.0:
        return 1
    if not isFlip(trial_type) and response == 1.0:
        return 2
    if not isFlip(trial_type) and response == -1.0:
        return 1
    return 5


def extractInfo(file, outputdir='.'):
    """
    Main Function to extract data
    """
    try:
        aacFile = pd.read_csv(file, low_memory = False,error_bad_lines=False)
        print list(aacFile.columns)
    except Exception as e:
        print "Error reading file.."
        print e
        return

    outputFileName = os.path.join(outputdir,'EXTRACT-' + os.path.basename(file) )



    header = []
    header.append('Trial')
    [ header.append('o1_' + str(x)) for x in range(0,2)] # Observation 1 // 1 for move till final position
    [ header.append('o2_' + str(x)) for x in range(0,2)] # Observation 2 // Condtion
    [ header.append('o3_' + str(x)) for x in range(0,2)] # Observation 3 // Position number and then final position
    [ header.append('u_' + str(x)) for x in range(0,2)]   # Action // Action call

    #outputfile.write(','.join(header) + '\n') # Write Header

    responseDictionary = {}
    outcomeDictionary = {}

    trial = 0
    final = []
    # Iterayte over trials
    for index,row in aacFile.iterrows():
        outputrow = []
        outputrow.append(index)

        firstPos = row['StartPos (starting position of the avatar)']
        finalPos = row['EndPos (end position of the avatar)']
        #outcome = outcomeDictionary[trial]

        obs1 = getObservation1(row) # o1
        obs2 = getObservation2(row) # o2
        obs3 = getObservation3(row) # o3
        u_ = getObservation3(row) # u

        [ outputrow.append(value) for value in obs1]
        [ outputrow.append(value) for value in obs2]
        [ outputrow.append(value) for value in obs3]
        [ outputrow.append(value) for value in u_ ]

        final.append(outputrow)

        print outputrow


    #print header
    finlapd = pd.DataFrame(final, columns=header)
    finlapd.to_csv(outputFileName,index = False)





if __name__ == "__main__":
    if len(sys.argv) > 1:
        print "Inputs:"
        print sys.argv
        file = sys.argv[1]
        outputdir = '.' # default output location
        try:
            outputdir = sys.argv[2]
        except IndexError:
            # Probably didn't enter an output location
            pass
    
        extractInfo(file, outputdir)
    else:
        print "No Inputs given, nust specify input file"
