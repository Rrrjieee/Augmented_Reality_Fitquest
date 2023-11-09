#BELOW IS ALL EXERCISE COUNTER LOGIC

#BICEP CURL UP 
def curl(angle, stage, ave, counter):
    if angle > 160:
        stage = "down"
    if angle < 30 and stage =='down':
        stage="up"
        counter +=1
        if inside > angle:
            inside = angle
    if angle > 30 and stage == "up":
        ave += inside
        inside = 31
        stage = "down"
        print(ave)
        print(counter)
    return stage, counter, ave

#SQUATS 
def squats(angle, ave, stage, counter):
    if angle <= 90:
        stage = "down"
    if angle > 160 and stage =='down':
        stage="up"
        counter +=1
        if inside > angle:
            inside = angle
    if angle < 160 and stage == 'up':
        ave += inside
        inside = 161
        stage = "down"
        print(ave)
    return stage, counter, ave

#PUSH-UP
def pushup(angle, angle2, ave, stage, counter):
    if angle <= 70:
        stage = "down"      
    elif stage =='down' and angle >= 160:
        stage="up"
        if angle2 < 160 and angle2 < 180:
            stage="wrong"
        else: 
            counter +=1     
        #   print(counter)
    if stage == 'up' and angle < 160:
        ave += inside
        inside = 161
        stage = "down"
        print(ave)
    return stage, counter, ave

#PLANK
def plank(angle, angle2, stage, counter):
    if angle < 90:
        stage = "adjust your arms"
        if angle2 < 170:
            stage="lower your hip position"
        elif angle2 >= 170:
            stage="down" 
            counter +=1
            print(counter)
    return stage, counter

#SIT-UPS
def situps(angle, ave, stage, counter):
    if angle > 120:
        stage = "down"
    if angle < 30 and stage =='down':
        stage="up"
        counter +=1
        if inside > angle:
            inside = angle
    if angle > 30 and stage == 'up':
        ave += inside
        inside = 31
        stage = "down"
        print(ave)
    return stage, counter, ave

#LUNGES
def lunges(angle, ave, stage, counter):
    if angle > 160:
        stage = "up"
    if stage =='up' and angle < 90:
        stage="down"
        counter +=1
    #   print(counter)
        if inside > angle:
            inside = angle
    if angle > 90 and stage == 'down':
        ave += inside
        inside = 91
        stage = "up"
        print(ave)
    return stage, counter, ave

#HIGH KNEES
def high_knees(angle, ave, stage, counter):
    if angle < 120:
        stage = "up"
    if stage =='up' and angle > 150:
        stage="down"
        counter +=1
    #   print(counter)
        if inside > angle:
            inside = angle
    if angle > 150 and stage == 'down':
        ave += inside
        inside = 151
        stage = "up"
        print(ave)
    return stage, counter, ave

#GLUTE BRIDGES
def glute_bridges(angle, ave, stage, counter):
    if angle < 120:
        stage = "down"
    if angle > 170 and stage =='down':
        stage="up"
        counter +=1
    #   print(counter)
        if inside > angle:
            inside = angle
    if angle < 170 and stage == 'up':
        ave += inside
        inside = 169
        stage = "down"
        print(ave)
    return stage, counter, ave