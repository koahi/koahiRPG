import random
import time
import sleekxmpp
import static as db

elapsed = 0
start = 0

class main:
    def __init__(self,parent):
        self.parent=parent
        self.messagable=True
        self.trackable=True
        self.active=False

        self.nameatk=0
        self.namedef=0
        self.name=0
        self.jid=0
        self.jidatk=0
        self.jiddef=0
        self.combat_out = []
        self.pdata={}

    def help(self, admin):
        return ""

    def message(self, msg, admin, ignored):
        if self.active and str(msg["mucnick"]) != u"":
            self.commands(msg, admin, ignored)

    def commands(self, msg, admin, ignored):

        if str(msg["body"]).lower().startswith(".") and msg["type"] == "groupchat":
            global elapsed
            global start
            elapsed = time.time() - start
            if elapsed > 1:

                #VIEW STATS
                if str(msg["body"]).lower().startswith(".stats") and msg["type"] == "groupchat":
                    jid = self.parent.jidList[str(msg["mucnick"])]
                    self.stats(jid, msg)

                #CREATE CHARACTER
                if str(msg["body"]).lower().startswith(".create") and msg["type"] == "groupchat":
                    jid = self.parent.jidList[str(msg["mucnick"])]
                    self.create(jid, msg)

                #HJID CHECK
                if str(msg["body"]).lower().startswith(".jid") and msg["type"] == "groupchat":
                    print self.parent.jidList.values()

            start = time.time()


    def combatset(self):
        self.nameatk, self.jidatk = self.jid_roll()

        while self.check(self.jidatk) == 0:
            self.nameatk, self.jidatk = self.jid_roll()
            print "ATK REROLLING" + self.jidatk

        self.namedef, self.jiddef = self.jid_roll()

        while self.check(self.jiddef) == 0 or self.jiddef == self.jidatk:
            self.namedef, self.jiddef = self.jid_roll()
            print "DEF REROLLING" + self.jiddef

        self.read_data(self.jidatk)
        level1 = int(self.pdata["LEVEL"])
        weapon1 = int(self.pdata["WEAPON"])
        effect1 = int(self.pdata["EFFECT"])
        self.read_data(self.jiddef)
        level2 = int(self.pdata["LEVEL"])
        weapon2 = int(self.pdata["WEAPON"])
        effect2 = int(self.pdata["EFFECT"])
        self.combat(level1, level2, weapon1, weapon2, effect1, effect2)


def combat(self, al, dl, aw, dw, ae, de):
    atkres = random.randint(al, 2*al) + random.randint(1,10)
    defres = random.randint(dl, 2*dl) + random.randint(1,10)

    if aw!=0:
        atkres += db.wlist[aw]['dmg']

    if dw!=0:
        defres += db.wlist[dw]['dmg']

    combatresult = atkres - defres
    print ("%s %i vs %s %i Result: %i" % (self.nameatk, al, self.namedef, dl, combatresult))

    if combatresult > 0:
        self.combat_out.append("\n%s[%i] %s %s[%i]" % (self.nameatk, atkres, random.choice(db.winp),
                                                       self.namedef, defres))
        self.combat_exp_gain(self.nameatk, self.namedef)
        self.level_check(self.jidatk, self.nameatk)

    elif combatresult <= 0:
        self.combat_out.append("\n%s[%i] %s %s[%i]" % (self.nameatk, atkres,
                                                       random.choice(db.losep), self.namedef, defres))
        self.combat_exp_gain(self.namedef, self.nameatk)
        self.level_check(self.jiddef, self.namedef)

    if ae == 1 and de == 1:
        self.weapon_decay(self.jidatk, self.nameatk)									#
        self.weapon_decay(self.jiddef, self.namedef)									#

    elif ae == 0 and de == 0:															#
        self.weapon_decay(self.jidatk, self.nameatk)									#
        self.weapon_decay(self.jiddef, self.namedef)									# caustic

    elif de == 1:																		# armor
        self.SKILL_caustic_armor(self.jidatk, self.nameatk, self.jiddef, self.namedef)	# effect
        self.weapon_decay(self.jiddef, self.namedef)									#

    elif ae == 1:																		#
        self.SKILL_caustic_armor(self.jiddef, self.namedef, self.jidatk, self.nameatk)	#
        self.weapon_decay(self.jidatk, self.nameatk)									#

    self.combat_report()


def combat_report(self):
    temp_str = ' '.join(self.combat_out)
    self.parent.channel_message(str(' '.join(self.combat_out)))
    self.combat_out = []


def timed_exp_gain(self):
    list = []
    for i in self.parent.jidList.keys():
        jid = str(self.parent.jidList[i])
        if self.check(jid) == 1 and i != "rpgbot" and not jid in list:
            self.read_data(jid)
            self.pdata["EXP"] += random.randint(1, 10) + random.randint(1, int(self.pdata["LEVEL"]))
            self.write_data(jid)
            self.level_check(jid, i)
            list.append(str(jid))


def timed_weapon_gain(self):
    self.name, self.jid = self.jid_roll()
    while self.check(self.jid) == 0:
        self.name, self.jid = self.jid_roll()
        print "WEAPON REOLLING " + self.jid

    self.read_data(self.jid)
    print "WEAPON GAIN " + self.jid

    if self.pdata["LEVEL"] <= 2:
        weapon_roll=random.randint(1,3)

    elif 3 <= self.pdata["LEVEL"] <= 4:
        weapon_roll=random.randint(4,6)

    elif 5 <= self.pdata["LEVEL"] <= 7:
        weapon_roll=random.randint(7,9)

    elif 8 <= self.pdata["LEVEL"] <= 10:
        weapon_roll=random.randint(10,16)

    if weapon_roll > self.pdata["WEAPON"]:
        self.pdata["WEAPON"] = weapon_roll
        self.pdata["WEAPON_DUR"] = int(db.wlist[weapon_roll]["dur"])
        self.write_data(self.jid)
        self.parent.channel_message("\n%s has gained a %s!" % (self.name, db.wlist[weapon_roll]["name"]))


def weapon_decay(self, jid, name):
    self.read_data(jid)
    if self.pdata["WEAPON"] != 0:
        if self.pdata["WEAPON_DUR"] <= 1:
            self.combat_out.append("\n%s's %s has broken!" % (name, db.wlist[self.pdata["WEAPON"]]['name']))
            self.pdata["WEAPON"] = 0
            self.pdata["WEAPON_DUR"] = 0
        else:
            self.pdata["WEAPON_DUR"] -= 1
        self.write_data(jid)


def SKILL_caustic_armor(self, jid1, name1, jid2, name2):
    self.read_data(jid1)
    if self.pdata["WEAPON"] != 0:
        if self.pdata["WEAPON_DUR"] <= 3:
            self.combat_out.append("\n%s's caustic armor destroys %s's weapon!" % (name2, name1))
            self.pdata["WEAPON"] = 0
            self.pdata["WEAPON_DUR"] = 0
        else:
            self.pdata["WEAPON_DUR"] -= 3
            self.combat_out.append("\n%s' caustic armor corrodes %s's weapon!" % (name2, name1))
        self.write_data(jid1)


def effects_decay(self):
    counter = 0
    for name in self.parent.jidList.keys():
        jid = str(self.parent.jidList[name])
        if self.check(jid):
            self.read_data(jid)
            if self.pdata["EFFECT"] != 0:
                if self.pdata["EFFECT_DUR"] == 1:
                    self.parent.channel_message("\n%s's %s has worn off!" % (name,
                                                                             db.elist[self.pdata["EFFECT"]]['name']))
                    self.pdata["EFFECT"] = 0
                    self.pdata["EFFECT_DUR"] = 0
                else:
                    self.pdata["EFFECT_DUR"] -= 1
                self.write_data(jid)


def timed_effects_gain(self):
    self.name, self.jid = self.jid_roll()
    while self.check(self.jid) == 0:
        self.name, self.jid = self.jid_roll()
        print "EFFECTS REOLLING " + self.jid
    self.read_data(self.jid)
    print "EFFECTS GAIN " + self.jid
    #self.wroll=random.randint(1,16)
    if self.pdata["EFFECT"] == 0:
        self.pdata["EFFECT"] = 1
        self.pdata["EFFECT_DUR"] = int(db.elist[self.pdata["EFFECT"]]["dur"])
        self.write_data(self.jid)
        self.parent.channel_message("\n%s is empowered with %s!" % (self.name, db.elist[1]['name']))


def stats(self, jid, msg):
    self.read_data(jid)
    if self.check(jid):
        level = str(self.pdata["LEVEL"])
        exp = self.pdata["EXP"]
        expl = self.pdata["EXP2L"]
        wins = str(self.pdata["WINS"])
        losses = str(self.pdata["LOSSES"])
        weaponn = str(db.wlist[self.pdata["WEAPON"]]["name"])
        weapond = str(db.wlist[self.pdata["WEAPON"]]["dur"])
        weaponcd = str(self.pdata["WEAPON_DUR"])
        effectn = str(db.elist[self.pdata["EFFECT"]]['name'])
        effectd = str(self.pdata["EFFECT_DUR"])
        output = [['{:<16}'.format('Level: ' + level),
                   '{:<23}'.format('Wins/Losses: ' + wins + '/' + losses),
                   'Exp: {0:,d} / {1:,d}'.format(exp, expl)],
                  ['{:<36}'.format('Weapon: '+weaponn+' ('+weaponcd+'/'+weapond+')'),
                   '{:<36}'.format('Effect: '+effectn+'('+effectd+')')]]
        out_row1 = "".join(word for word in output[0])
        out_row2 = "".join(word for word in output[1])
        self.parent.channel_message("\n" + str(out_row1) + "\n" + str(out_row2).strip("\n"))

    elif self.check(jid)==0:
        self.parent.channel_message(str(msg["mucnick"]) + ": Please use .create to create your own character!")


def level_check(self, jid, name):
    self.read_data(jid)
    if int(self.pdata["EXP"]) > int(self.pdata["EXP2L"]):
        print "LEVEL CHECK " + str(jid)
        self.pdata["LEVEL"] += 1
        self.pdata["EXP"] = 0
        self.pdata["EXP2L"] = self.pdata["LEVEL"]*self.pdata["LEVEL"]*200
        self.parent.channel_message("\n%s has reached level %i!" % (name, self.pdata["LEVEL"]))
    self.write_data(jid)


def combat_exp_gain(self, namew, namel):
    jidw = self.parent.jidList[namew]
    jidl = self.parent.jidList[namel]
    self.read_data(jidl)
    exp_gain = random.randint(int(self.pdata["LEVEL"]) * 10, int(self.pdata["LEVEL"]) * 20)
    self.pdata["EXP"] -= exp_gain

    if self.pdata["EXP"] < 0:
        self.pdata["EXP"] = 0

    self.pdata["LOSSES"] += 1
    self.write_data(jidl)
    self.read_data(jidw)
    self.pdata["EXP"] += exp_gain
    self.pdata["WINS"] += 1
    self.write_data(jidw)
    self.combat_out.append("for " + str(exp_gain) + " exp!")


def jid_roll(self):
    roll = random.randint(0, len(self.parent.jidList.keys())-1)
    roll_name = self.parent.jidList.keys()[roll]
    roll_jid = self.parent.jidList[roll_name]
    return roll_name, roll_jid


def check(self, jid):
    try:
        with open("/home/pi/koahiRPG/pfiles/"+jid+".txt") as f:
            return 1
    except IOError:
        return 0


def read_data(self, jid):
    self.pdata = {}
    try:
        with open("/home/pi/koahiRPG/pfiles/" + jid + ".txt") as f:
            for line in f:
                split_line = line.split(":")
                self.pdata[split_line[0]] = int(split_line[1])
    except IOError:
        print "NO FILE FOUND"


def create(self, jid, msg):
    self.read_data(jid)
    if self.check(jid):
        self.parent.channel_message(str(msg["mucnick"]) + ": Your character already exists.")
    else:
        with open("/home/pi/koahiRPG/pfiles/" + jid + ".txt" ,"w+") as f:
            f.write("LEVEL:1\n")
            f.write("EXP:0\n")
            f.write("EXP2L:200\n")
            f.write("WEAPON:0\n")
            f.write("WEAPON_DUR:0\n")
            f.write("WINS:0\n")
            f.write("LOSSES:0\n")
            f.write("EFFECT:0\n")
            f.write("EFFECT_DUR:0\n")

        self.parent.channel_message(str(msg["mucnick"])+": Your character has been created!")


def write_data(self, jid):
    with open("/home/pi/koahiRPG/pfiles/"+jid+".txt" ,"w") as f:
        for attr in self.pdata.keys():
            f.write(str(attr)+":"+str(self.pdata[attr])+"\n")
