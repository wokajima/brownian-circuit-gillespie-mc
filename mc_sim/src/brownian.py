import math
import random
import logging as lg
import numpy as np
import pandas as pd

if __name__ == "__main__":
    import config
else:
    from . import config

lg.basicConfig(level=lg.WARNING, format="%(levelname)s:%(message)s")

#入力状態から終了状態に初めて達するまでの軌道を計算する
#まず初期状態を生成する。
def initialize(M,name):
    job = "config."+name+"."
    initialized_state = random.choice(eval(job+"initial"))
    for i in range(M-1):
        initialized_state = initialized_state | random.choice(eval(job+"secondary")) << eval(job+"Base_length")*i+eval(job+"Mod_length")
    lg.debug("output is")
    lg.debug(bin(initialized_state).zfill(eval(job+"Base_length")*M+4))
    return initialized_state

def initialized_states_array(M,name):
    states_array = []
    job = "config."+name+"."
    lg.debug("name is setted as "+name)
    states_array = eval(job+"initial")
    for m in range(M-1):
        states_array = secondary_module_adding(m,name,states_array)
    return states_array

def secondary_module_adding(M,name,array):
    list = []
    job = "config."+name+"."
    add_list = eval(job+"secondary")
    base_l =eval(job+"Base_length")
    mod_l = eval(job+"Mod_length")
    for state in array:
        for add in add_list:
            list.append(state | add << base_l*M+mod_l)
    return list

def check_init(M,name,state):
    watcher = True
    eyeball = False
    base_l = eval("config."+name+"."+"Base_length") #シフトさせる長さ
    job = "config."+name+".secondary"
    for m in range(M):
        eyeball = False
        for check_state in eval(job):
            eyeball = eyeball or ((state&(check_state << base_l*m+2)) == (check_state << base_l*m+2))
        watcher = watcher and eyeball
    if watcher:lg.debug(str(bin(state).zfill(base_l*M+4))+" is initial state.")
    return watcher

def check_finish(M,name,state):
    watcher = True
    eyeball = False
    base_l = eval("config."+name+"."+"Base_length") #シフトさせる長さ
    job = "config."+name+".final"
    for m in range(M):
        if name=="full_adder" and m==M-1:
            eyeball = False
            for check_state in eval("config."+name+".edge_final"):
                eyeball = eyeball or ((state&(check_state << base_l*m)) == (check_state << base_l*m))
            watcher = watcher and eyeball
        else:
            eyeball = False
            for check_state in eval(job):
                eyeball = eyeball or ((state&(check_state << base_l*m)) == (check_state << base_l*m))
            watcher = watcher and eyeball
    if watcher: lg.debug("Finish state: "+str(bin(state).zfill(base_l*M+4)))
    return watcher

def check_forward(M,name,state):
    count = 0
    job = "config."+name+".forward"
    base_l = eval("config."+name+"."+"Base_length") #シフトさせる長さ
    for m in range(M):
        for check in eval(job):
            check_state = (state & (check<<(base_l*m)))>>(base_l*m)
            lg.debug(bin(state).zfill(base_l*M+4)) #デバッグ用
            lg.debug(bin(check).zfill(base_l*M+4)) #デバッグ用
            if check_state == check:
                count += 1
                lg.debug("fit")
    return count

def check_backward(M,name,state):
    count = 0
    base_l = eval("config."+name+"."+"Base_length") #シフトさせる長さ
    job = "config."+name+".backward"
    for m in range(M):
        for check in eval(job):
            check_state = (state & (check<<(base_l*m)))>>(base_l*m)
            lg.debug(bin(state).zfill(base_l*M+4)) #デバッグ用
            lg.debug(bin(check).zfill(base_l*M+4)) #デバッグ用
            if check_state == check:
                count += 1
                lg.debug("fit")
    return count

def gen_next(M,name,state,rate_forward=1,rate_backward=1):
    rand_s = random.random() #状態を決定する乱数
    base_l = eval("config."+name+"."+"Base_length") #シフトさせる長さ
    q = rate_forward * check_forward(M,name,state) + rate_backward * check_backward(M,name,state)
    lg.info("total rate is "+str(q))
    lg.info("random number is "+str(rand_s))
    lg.info("compare random number with: "+str((rate_forward * check_forward(M,name,state))/q))
    total = 0
    if rand_s < (rate_forward * check_forward(M,name,state))/q:
        which = ".forward"
        rate = rate_forward
    else:
        which = ".backward"
        rate = rate_backward
        total += rate_forward * check_forward(M,name,state)
    lg.info("this transition is "+which)
    check = eval("config."+name+which)
    transition = eval("config."+name+".transition")
    lg.info("now state is")
    lg.info(str(bin(state).zfill(base_l*M+4)))
    for m in range(M):
        lg.info("now checking module is "+str(m))
        for i in range(len(check)):
            if(check[i] == (state & (check[i]<<(base_l*m)))>>(base_l*m)):
                lg.info("check")
                lg.info(bin(check[i]<<(base_l*m)).zfill(base_l*M+4)) #デバッグ用
                lg.info("=chech ?")
                lg.info(bin((state & (check[i]<<(base_l*m)))).zfill(base_l*M+4)) #デバッグ用
                total += rate
                lg.info("compare this with random number: "+str(total/q))
            if(rand_s < total/q):
                lg.info("TRANSITION HAPPENS")
                lg.info("now state is")
                lg.info(bin(state).zfill(base_l*M+4)) #デバッグ用
                lg.info("transition is")
                lg.info(bin(transition[i]<<(base_l*m)).zfill(base_l*M+4)) #デバッグ用
                next_state = state^(transition[i]<<(base_l*m))
                lg.info("next state is")
                lg.info(bin(next_state).zfill(base_l*M+4))
                break
        else:
            continue
        break
    return next_state

def rev_gen_next(M,name,state,rate_forward=1,rate_backward=1):
    rand_s = random.random() #状態を決定する乱数
    base_l = eval("config."+name+"."+"Base_length") #シフトさせる長さ
    q = rate_forward * check_forward(M,name,state) + rate_backward * check_backward(M,name,state)
    lg.info("total rate is "+str(q))
    lg.info("random number is "+str(rand_s))
    lg.info("compare random number with: "+str((rate_forward * check_forward(M,name,state))/q))
    total = 0
    if rand_s < (rate_backward * check_backward(M,name,state))/q:
        which = ".backward"
        rate = rate_backward
    else:
        which = ".forward"
        rate = rate_forward
        total += rate_backward * check_backward(M,name,state)
    lg.info("this transition is "+which)
    check = eval("config."+name+which)
    transition = eval("config."+name+".transition")
    lg.info("now state is")
    lg.info(str(bin(state).zfill(base_l*M+4)))
    for m in range(M):
        lg.info("now checking module is "+str(m))
        for i in range(len(check)):
            if(check[i] == (state & (check[i]<<(base_l*m)))>>(base_l*m)):
                lg.info("check")
                lg.info(bin(check[i]<<(base_l*m)).zfill(base_l*M+4)) #デバッグ用
                lg.info("=chech ?")
                lg.info(bin((state & (check[i]<<(base_l*m)))).zfill(base_l*M+4)) #デバッグ用
                total += rate
                lg.info("compare this with random number: "+str(total/q))
            if(rand_s < total/q):
                lg.info("TRANSITION HAPPENS")
                lg.info("now state is")
                lg.info(bin(state).zfill(base_l*M+4)) #デバッグ用
                lg.info("transition is")
                lg.info(bin(transition[i]<<(base_l*m)).zfill(base_l*M+4)) #デバッグ用
                next_state = state^(transition[i]<<(base_l*m))
                lg.info("next state is")
                lg.info(bin(next_state).zfill(base_l*M+4))
                break
        else:
            continue
        break
    return next_state

def next_state_array(M,name,state):
    states_array = []
    base_l = eval("config."+name+"."+"Base_length") #シフトさせる長さ
    which=".forward"
    check = eval("config."+name+which)
    transition = eval("config."+name+".transition")
    lg.info("now state is")
    lg.info(str(bin(state).zfill(base_l*M+4)))
    for m in range(M):
        lg.info("now checking module is "+str(m))
        for i in range(len(check)):
            if(check[i] == (state & (check[i]<<(base_l*m)))>>(base_l*m)):
                lg.info("check")
                lg.info(bin(check[i]<<(base_l*m)).zfill(base_l*M+4)) #デバッグ用
                lg.info("=chech ?")
                lg.info(bin((state & (check[i]<<(base_l*m)))).zfill(base_l*M+4)) #デバッグ用
                states_array.append(state^(transition[i]<<(base_l*m)))
    which=".backward"
    check = eval("config."+name+which)
    for m in range(M):
        lg.info("now checking module is "+str(m))
        for i in range(len(check)):
            if(check[i] == (state & (check[i]<<(base_l*m)))>>(base_l*m)):
                lg.info("check")
                lg.info(bin(check[i]<<(base_l*m)).zfill(base_l*M+4)) #デバッグ用
                lg.info("=chech ?")
                lg.info(bin((state & (check[i]<<(base_l*m)))).zfill(base_l*M+4)) #デバッグ用
                states_array.append(state^(transition[i]<<(base_l*m)))
    return states_array


#状態ビット列から論理状態を取り出す
def trans_logic(M,name,state):
    logic = ""
    base_l = eval("config."+name+"."+"Base_length") #シフトさせる長さ
    for m in reversed(range(M)):
        logic += "<"+str(m+1)+"]"
        for i in reversed(range(len(eval("config."+name+".logic_state")))):
            check = state & 0b1<<(base_l*m+i)
            if check:
                check = check>>(base_l*m)
                logic += eval("config."+name+".logic_state["+str(bin(check))+"]") + ","
    return logic
#いらないやつを省く
def trans_logic_short(M,name,state):
    logic = ""
    base_l = eval("config."+name+"."+"Base_length") #シフトさせる長さ
    mod_l = eval("config."+name+"."+"Mod_length")
    for m in reversed(range(M)):
        logic += "<"+str(m+1)+"]"
        for i in reversed(range(mod_l)):
            check = state & 0b1<<(base_l*m+i)
            check = check>>(base_l*m)
            if check and check in eval("config."+name+".logic_state_adder"):
                logic += eval("config."+name+".logic_state_adder["+str(bin(check))+"]") + ","
    return logic

#特定の論理変数だけ取ってくる
def trans_num(M,name,state,shift=0):
    num = 0
    base_l = eval("config."+name+"."+"Base_length") #シフトさせる長さ
    if name == "product_adder":
        for m in range(M):
            if state&(0b1<<(base_l*m+shift)):num += 2**m
    if name == "precede_adder":
        for m in range(M):
            if state&(0b1<<(base_l*m+shift)):num += 2**m
    return num

def test_trajectory(M,name,rate_forward=1,rate_backward=1):
    orbit = [] #軌跡のリスト,動作確認用
    current_state = 0b0 #回路の状態
    next_state = 0b0 #回路の次の状態
    dt = 0 #状態の滞在時間
    dt_list = [] #返す時間リスト,動作確認用
    q_list = []
    time = 0 #返す時間
    jump = 0 #返す遷移総回数
    T=10000000 #経路の最大観測時間
    #初期状態の生成
    initial_state = initialize(M,name) #初期状態
    current_state =initial_state
    orbit.append(current_state)
    #経路の生成
    while not check_finish(M,name,next_state) and (time <= T):
        rand_t = random.random() #滞在時間を決定する乱数
        dt = 0
        q = 0
        q = rate_forward * check_forward(M,name,current_state) + rate_backward * check_backward(M,name,current_state)
        #次の遷移状態を決定する
        next_state = gen_next(M,name,current_state,rate_forward,rate_backward)
        #現在の状態の滞在時間を決定する
        dt = 1/q * math.log(1/rand_t)
        dt_list.append(dt)
        time += dt
        #遷移を一回足す
        jump += 1
        current_state = next_state
        q_list.append(q)
        orbit.append(current_state)
    return [initial_state,dt_list,q_list,orbit]

def sim_test(M,name,rate_forward=1,rate_backward=1):
    #データの取得
    #経路の取得
    time = [] #滞在時間の格納リスト
    dt_list = [0]
    q = [] #qの格納リスト
    Q = [0]
    orbit = [] #軌道
    #経路の生成
    [initial_state,time,q,orbit] = test_trajectory(M,name,rate_forward,rate_backward)
    if initial_state == orbit[0]:
        #csvファイルの保存
        orbit = [trans_logic(M,name,state) for state in orbit]
        print(orbit)
        dt_list += time
        Q += q
        orbit = np.array(orbit)
        dt_list = np.array(dt_list)
        Q = np.array(Q)
        data = [[orbit[i],dt_list[i],Q[i]] for i in range(len(orbit))]
        data_frame = pd.DataFrame(data)
        data_frame.to_csv('./'+name+str(M)+'test_orbit.csv',header=False,index=False)
    print("test cases were closed!")

if __name__ == "__main__":
    sim_test(2,"full_adder")
    sim_test(2,"poduct_adder")