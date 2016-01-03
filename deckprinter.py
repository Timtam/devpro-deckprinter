import argparse
import os
import os.path
import re
import sqlite3
import sys
BLUESCALE=0x1000000
REDSCALE=0x10000
ATTRIBUTE_EARTH=0x01
ATTRIBUTE_WATER=0x02
ATTRIBUTE_FIRE=0x04
ATTRIBUTE_WIND=0x08
ATTRIBUTE_LIGHT=0x10
ATTRIBUTE_DARK=0x20
ATTRIBUTE_DEVINE=0x40
RACE_WARRIOR=0x1
RACE_SPELLCASTER=0x2
RACE_FAIRY=0x4
RACE_FIEND=0x8
RACE_ZOMBIE=0x10
RACE_MACHINE=0x20
RACE_AQUA=0x40
RACE_PYRO=0x80
RACE_ROCK=0x100
RACE_WINDBEAST=0x200
RACE_PLANT=0x400
RACE_INSECT=0x800
RACE_THUNDER=0x1000
RACE_DRAGON=0x2000
RACE_BEAST=0x4000
RACE_BEASTWARRIOR=0x8000
RACE_DINOSAUR=0x10000
RACE_FISH=0x20000
RACE_SEASERPENT=0x40000
RACE_REPTILE=0x80000
RACE_PSYCHO=0x100000
RACE_DEVINE=0x200000
RACE_CREATORGOD=0x400000
RACE_PHANTOMDRAGON=0x800000
TYPE_MONSTER=0x1
TYPE_SPELL=0x2
TYPE_TRAP=0x4
TYPE_NORMAL=0x10
TYPE_EFFECT=0x20
TYPE_FUSION=0x40
TYPE_RITUAL=0x80
TYPE_TRAPMONSTER=0x100
TYPE_SPIRIT=0x200
TYPE_UNION=0x400
TYPE_DUAL=0x800
TYPE_TUNER=0x1000
TYPE_SYNCHRO=0x2000
TYPE_TOKEN=0x4000
TYPE_QUICKPLAY=0x10000
TYPE_CONTINUOS=0x20000
TYPE_EQUIP=0x40000
TYPE_FIELD=0x80000
TYPE_COUNTER=0x100000
TYPE_FLIP=0x200000
TYPE_TOON=0x400000
TYPE_XYZ=0x800000
TYPE_PENDULUM=0x1000000
RACE_INDEX={RACE_WARRIOR:1020,
            RACE_SPELLCASTER:1021,
            RACE_FAIRY:1022,
            RACE_FIEND:1023,
            RACE_ZOMBIE:1024,
            RACE_MACHINE:1025,
            RACE_AQUA:1026,
            RACE_PYRO:1027,
            RACE_ROCK:1028,
            RACE_WINDBEAST:1029,
            RACE_PLANT:1030,
            RACE_INSECT:1031,
            RACE_THUNDER:1032,
            RACE_DRAGON:1033,
            RACE_BEAST:1034,
            RACE_BEASTWARRIOR:1035,
            RACE_DINOSAUR:1036,
            RACE_FISH:1037,
            RACE_SEASERPENT:1038,
            RACE_REPTILE:1039,
            RACE_PSYCHO:1040,
            RACE_DEVINE:1041,
            RACE_CREATORGOD:1042,
            RACE_PHANTOMDRAGON:1043}
ATTRIBUTE_INDEX={ATTRIBUTE_EARTH:1010,
                 ATTRIBUTE_WATER:1011,
                 ATTRIBUTE_FIRE:1012,
                 ATTRIBUTE_WIND:1013,
                 ATTRIBUTE_LIGHT:1014,
                 ATTRIBUTE_DARK:1015,
                 ATTRIBUTE_DEVINE:1016}
TYPE_INDEX={TYPE_NORMAL:1054,
            TYPE_EFFECT:1055,
            TYPE_FUSION:1056,
            TYPE_RITUAL:1057,
            TYPE_TRAPMONSTER:1058,
            TYPE_SPIRIT:1059,
            TYPE_UNION:1060,
            TYPE_DUAL:1061,
            TYPE_TUNER:1062,
            TYPE_SYNCHRO:1063,
            TYPE_TOKEN:1064,
            TYPE_QUICKPLAY:1066,
            TYPE_CONTINUOS:1067,
            TYPE_EQUIP:1068,
            TYPE_FIELD:1069,
            TYPE_COUNTER:1070,
            TYPE_FLIP:1071,
            TYPE_TOON:1072,
            TYPE_XYZ:1073,
            TYPE_PENDULUM:1074}
def _print(str):
 str=str.strip()
 str=str.replace('\t','  ')
 str=str+('\r\n' if args.windows else '\n')
 sys.stdout.write(str)
def DResult(cursor):
 res={}
 rows=cursor.fetchall()
 if len(rows)==0: return res
 for row in rows:
  rowres={}
  for colid in range(0, len(row)):
   rowres[cursor.description[colid][0]]=row[colid]
  res[rowres['id']]=rowres
 return res
def GetIdTuple(deck):
 lid=[]
 for line in deck:
  line=line.strip()
  try:
   line=int(line)
   if line in lid: continue
   lid.append(line)
  except ValueError:
   pass
 tid=tuple(lid)
 sid='?,'*len(lid)
 sid=sid[:-1]
 return tid,sid
def GetTypeDescriptor(type):
 rtype=''
 types=TYPE_INDEX.keys()
 types.sort()
 types.reverse()
 for dtype in types:
  if type&dtype==dtype:
   rtype=rtype+' / %s'%Messages['system'][TYPE_INDEX[dtype]]
 return rtype
def MyDirectory():
 if hasattr(sys, "frozen") and sys.frozen in ["console_exe", "windows_exe"]:
  Path=os.path.dirname(sys.executable)
 else:
  Path = os.path.dirname(os.path.abspath(__file__))
 bdir=os.path.isdir(Path)
 while not bdir:
  Path=os.path.abspath(Path+'/..')
  bdir=os.path.isdir(Path)
 return Path
def ParsePendulumLevel(rank):
 bluerank=rank/BLUESCALE
 rank=rank-bluerank*BLUESCALE
 redrank=rank/REDSCALE
 rank=rank-redrank*REDSCALE
 return (bluerank,redrank,rank)
def ParseStrings(strings):
 ore=re.compile("^!(\w+) (\d+) (.*)$")
 messages={}
 with open(strings,'r') as fstrings:
  for line in fstrings.readlines():
   line=line.strip()
   match=ore.match(line)
   if match:
    group=match.group(1)
    number=int(match.group(2))
    text=match.group(3)
    if group in messages: messages[group][number]=text
    else: messages[group]={number:text}
 return messages
def ParseDeck(deckdata,cursor):
 decklistmain={TYPE_MONSTER:{},TYPE_SPELL:{},TYPE_TRAP:{}}
 decklistextra={}
 decklistside={TYPE_MONSTER:{},TYPE_SPELL:{},TYPE_TRAP:{}}
 idtuple,idstring=GetIdTuple(deckdata)
 data=cursor.execute('select datas.id, datas.type, datas.attribute, datas.level, datas.atk, datas.def, datas.race, texts.name, texts.desc from datas, texts where datas.id in (%s) and texts.id in (%s) and datas.id=texts.id'%(idstring,idstring),idtuple*2)
 data=DResult(cursor)
 decktype=''
 for line in deckdata:
  line=line.strip()
  try:
   line=int(line)
   if not line in data:
    _print('Unable to find card %d in database'%line)
    continue
   carddata=data[line]
   if carddata['type']&TYPE_TRAP==TYPE_TRAP: type=TYPE_TRAP
   elif carddata['type']&TYPE_SPELL==TYPE_SPELL: type=TYPE_SPELL
   elif carddata['type']&TYPE_MONSTER==TYPE_MONSTER: type=TYPE_MONSTER
   if carddata['level']>12:
    level=ParsePendulumLevel(carddata['level'])
   else:
    level=(0,0,carddata['level'])
   text=carddata['desc'].replace('\n','\n\t\t')
   if decktype=='main':
    if 'c%s'%line in decklistmain[type]: decklistmain[type]['c%s'%line]['count']=decklistmain[type]['c%s'%line]['count']+1
    else: decklistmain[type]['c%s'%line]={'count':1,'name':carddata['name'].encode('utf-8'),'text':text.encode('utf-8'),'atk':carddata['atk'],'def':carddata['def'],'race':carddata['race'], 'attribute':carddata['attribute'],'type':carddata['type']-type,'level':level}
   elif decktype=='extra':
    if 'c%s'%line in decklistextra: decklistextra['c%s'%line]['count']=decklistextra['c%s'%line]['count']+1
    else: decklistextra['c%s'%line]={'count':1,'name':carddata['name'].encode('utf-8'),'text':text.encode('utf-8'),'atk':carddata['atk'],'def':carddata['def'],'race':carddata['race'],'attribute':carddata['attribute'],'type':carddata['type']-type,'level':level}
   elif decktype=='side':
    if 'c%s'%line in decklistside[type]: decklistside[type]['c%s'%line]['count']=decklistside[type]['c%s'%line]['count']+1
    else: decklistside[type]['c%s'%line]={'count':1,'name':carddata['name'].encode('utf-8'),'text':text.encode('utf-8'),'atk':carddata['atk'],'def':carddata['def'],'race':carddata['race'], 'attribute':carddata['attribute'],'type':carddata['type']-type,'level':level}
  except ValueError:
   if line.startswith('#main'): decktype='main'
   elif line.startswith('#extra'): decktype='extra'
   elif line.startswith('!side'): decktype='side'
   else: pass
 return (decklistmain, decklistextra, decklistside)
def PrintDeck(deck):
 output=Messages['system'][1330]+' {main}\n'+Messages['system'][70]+': {mainmonsters}\n'
 mainmonsters=0
 for card in deck[0][TYPE_MONSTER].keys():
  output=output+'\t{%s[count]}x {%s[name]}'%(card,card)+(' ('+card+')' if args.debug else '')+'\n\t\t{ATK} {%s[atk]}, {DEF} {%s[def]}, {level} {%s[level][2]}'%(card,card,card)+(', {pendulum}: {%s[level][0]}; {%s[level][1]}'%(card,card) if deck[0][TYPE_MONSTER][card]['level'][0]>0 else '')+'\n\t\t'+Messages['system'][1120]+': '+Messages['system'][ATTRIBUTE_INDEX[deck[0][TYPE_MONSTER][card]['attribute']]]+GetTypeDescriptor(deck[0][TYPE_MONSTER][card]['type'])+'\n\t\t'+Messages['system'][1121]+': '+Messages['system'][RACE_INDEX[deck[0][TYPE_MONSTER][card]['race']]]+'\n\t\t{%s[text]}\n'%card
  mainmonsters=mainmonsters+deck[0][TYPE_MONSTER][card]['count']
 output=output+Messages['system'][71]+': {mainspells}\n'
 mainspells=0
 for card in deck[0][TYPE_SPELL].keys():
  output=output+'\t{%s[count]}x {%s[name]}'%(card,card)+(' ('+card+')' if args.debug else '')+'\n\t\t'+Messages['system'][1120]+': '+Messages['system'][1051]+GetTypeDescriptor(deck[0][TYPE_SPELL][card]['type'])+'\n\t\t{%s[text]}\n'%card
  mainspells=mainspells+deck[0][TYPE_SPELL][card]['count']
 output=output+Messages['system'][72]+': {maintraps}\n'
 maintraps=0
 for card in deck[0][TYPE_TRAP].keys():
  output=output+'\t{%s[count]}x {%s[name]}'%(card,card)+(' ('+card+')' if args.debug else '')+'\n\t\t'+Messages['system'][1120]+': '+Messages['system'][1052]+GetTypeDescriptor(deck[0][TYPE_TRAP][card]['type'])+'\n\t\t{%s[text]}\n'%card
  maintraps=maintraps+deck[0][TYPE_TRAP][card]['count']
 output=output+Messages['system'][1331]+' {extra}\n'
 extra=0
 for card in deck[1].keys():
  output=output+'\t{%s[count]}x {%s[name]}'%(card,card)+(' ('+card+')' if args.debug else '')+'\n\t\t{ATK} {%s[atk]}, {DEF} {%s[def]}, {level} {%s[level][2]}'%(card,card,card)+(', {pendulum}: {%s[level][0]}; {%s[level][1]}'%(card,card) if deck[1][card]['level'][0]>0 else '')+'\n\t\t'+Messages['system'][1120]+': '+Messages['system'][ATTRIBUTE_INDEX[deck[1][card]['attribute']]]+GetTypeDescriptor(deck[1][card]['type'])+'\n\t\t'+Messages['system'][1121]+': '+Messages['system'][RACE_INDEX[deck[1][card]['race']]]+'\n\t\t{%s[text]}\n'%card
  extra=extra+deck[1][card]['count']
 output=output+Messages['system'][1332]+' {side}\n'+Messages['system'][70]+': {sidemonsters}\n'
 sidemonsters=0
 for card in deck[2][TYPE_MONSTER].keys():
  output=output+'\t{%s[count]}x {%s[name]}'%(card,card)+(' ('+card+')' if args.debug else '')+'\n\t\t{ATK} {%s[atk]}, {DEF} {%s[def]}, {level} {%s[level][2]}'%(card,card,card)+(', {pendulum}: {%s[level][0]}; {%s[level][1]}'%(card,card) if deck[2][TYPE_MONSTER][card]['level'][0]>0 else '')+'\n\t\t'+Messages['system'][1120]+': '+Messages['system'][ATTRIBUTE_INDEX[deck[2][TYPE_MONSTER][card]['attribute']]]+GetTypeDescriptor(deck[2][TYPE_MONSTER][card]['type'])+'\n\t\t'+Messages['system'][1121]+': '+Messages['system'][RACE_INDEX[deck[2][TYPE_MONSTER][card]['race']]]+'\n\t\t{%s[text]}\n'%card
  sidemonsters=sidemonsters+deck[2][TYPE_MONSTER][card]['count']
 output=output+Messages['system'][71]+': {sidespells}\n'
 sidespells=0
 for card in deck[2][TYPE_SPELL].keys():
  output=output+'\t{%s[count]}x {%s[name]}'%(card,card)+(' ('+card+')' if args.debug else '')+'\n\t\t'+Messages['system'][1120]+': '+Messages['system'][1051]+GetTypeDescriptor(deck[2][TYPE_SPELL][card]['type'])+'\n\t\t{%s[text]}\n'%card
  sidespells=sidespells+deck[2][TYPE_SPELL][card]['count']
 output=output+Messages['system'][72]+': {sidetraps}\n'
 sidetraps=0
 for card in deck[2][TYPE_TRAP].keys():
  output=output+'\t{%s[count]}x {%s[name]}'%(card,card)+(' ('+card+')' if args.debug else '')+'\n\t\t'+Messages['system'][1120]+': '+Messages['system'][1052]+GetTypeDescriptor(deck[2][TYPE_TRAP][card]['type'])+'\n\t\t{%s[text]}\n'%card
  sidetraps=sidetraps+deck[2][TYPE_TRAP][card]['count']
 if args.windows:
  output=output.replace('\n','\r\n')
 dcont=dict(deck[0][TYPE_MONSTER],**deck[1])
 dcont.update(deck[0][TYPE_SPELL])
 dcont.update(deck[0][TYPE_TRAP])
 dcont.update(deck[2][TYPE_MONSTER])
 dcont.update(deck[2][TYPE_SPELL])
 dcont.update(deck[2][TYPE_TRAP])
 main=mainmonsters+mainspells+maintraps
 side=sidemonsters+sidespells+sidetraps
 ATK=Messages['system'][1322]
 DEF=Messages['system'][1323]
 level=Messages['system'][1324]
 pendulum=Messages['system'][1074]
 _print(output.format(main=main, side=side, extra=extra, mainmonsters=mainmonsters, mainspells=mainspells, maintraps=maintraps, sidemonsters=sidemonsters, sidespells=sidespells, sidetraps=sidetraps, ATK=ATK, DEF=DEF, level=level, pendulum=pendulum, **dcont))
parser=argparse.ArgumentParser()
parser.add_argument("deck",help="deck name without path and extension or - to create a deck list of all available decks",type=str)
parser.add_argument("-d","--debug",help="print debug information, such as the card id",action="store_true")
parser.add_argument("-D","--database",help="full path of the cards.cdb file, default location is the programs containing directory or the DevPro path if specified",type=str)
parser.add_argument("-p","--path",help="defines the DevPro path if this file isn't currently located there",type=str)
parser.add_argument("-s","--strings",help="full path of the strings.conf file, default location is the programs containing directory or the DevPro path if specified",type=str)
parser.add_argument("-w","--windows",help="output formatted in windows-style (line-endings changed)",action="store_true")
args=parser.parse_args()
if args.path:
 iam=os.path.abspath(args.path)
 if not os.path.exists(iam):
  _print('Unable to find DevPro directory: %s'%iam)
  sys.exit()
else:
 iam=MyDirectory()
dbpath=(args.database if args.database else os.path.join(iam,"cards.cdb"))
strpath=(args.strings if args.strings else os.path.join(iam,"strings.conf"))
if not os.path.exists(dbpath):
 _print('Unable to find database file: %s'%dbpath)
 sys.exit()
if not os.path.exists(strpath):
 _print('Unable to find string file: %s'%strpath)
 sys.exit()
db=sqlite3.connect(dbpath)
cursor=db.cursor()
Messages=ParseStrings(strpath)
if args.deck=='-':
 decklist=os.listdir(os.path.join(iam,'deck'))
else:
 decklist=[]
 if not os.path.exists(os.path.join(iam,'deck',args.deck+'.ydk')):
  _print('Deck %s doesn\'t exist'%args.deck)
  sys.exit()
 decklist.append(args.deck+'.ydk')
for deck in decklist:
 with open(os.path.join(iam,'deck',deck),'r') as odeck:
  ldeck=odeck.readlines()
  _print(os.path.splitext(deck)[0]+':')
  ddeck=ParseDeck(ldeck,cursor)
  PrintDeck(ddeck)
sys.exit()