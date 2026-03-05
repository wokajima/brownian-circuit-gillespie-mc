import networkx as nx
import matplotlib.pyplot as plt

#全加算器を定義する変数
#遷移と状態を定義している

#状態はワイヤーに対応した1bitを複数桁用意した状態変数で記述される
#粒子がある場合1,ない場合0となる
#例えば0~4のワイヤーのうちワイヤー0と2にある状態は、0b00101、で表される

#遷移は1の場所を移す論理演算で記述される
#例えば0と2のトークンを4と5に移すとき、XOR0b11101を作用させる
#生成消滅演算子を作用させていると考えられる

#論理変数はA,B,C(comming carry),X(result),G(going carry)

#全てのワイヤーは次のようになる
#入力
#A,notA,B,notB,C,notC
#一段目出力
#A xor B, not(A xor B)
#A and B, not(A and B)
#二段目出力
#X, notX:X = A xor B xor C
#(A xor B) and C, not((A xor B) and C)
#三段目出力
#G, notG,
#E and(C and D), E and not(C and D), notE and (C and D), notE and not(C and D)
#全てで20bitの変数になる
#GとCが先頭と最後尾にきていて桁上げが自然に実装されている
#二桁目以降はCを除いた18bitを<<(18N+2) (N=1,2...)して結合すればよい
# S_N << 18N-16 | S_(N-1) << 18N-34 | ... | S_2 << 18+2 | S_1

Mod_length = 20     #モジュール全体の状態数
Base_length = 18    #桁上がり/桁上げを除いた状態数
Cjoin_num = 12      #C-joinゲートの数

logic_state = {0b1:"not C",
               0b1<<1:"C",
               0b1<<2:"not B",
               0b1<<3:"B",
               0b1<<4:"not A",
               0b1<<5:"A",#入力
               0b1<<6:"not(A xor B)",
               0b1<<7:"A xor B",#X方向の一段目出力
               0b1<<8:"not(A and B)",
               0b1<<9:"A and B",#G方向の一段目出力
               0b1<<10:"not((A xor B) and C)",
               0b1<<11:"(A xor B) and C",#桁上がりの移動
               0b1<<12:"not(A and B) and not((A xor B) and C)",
               0b1<<13:"(A and B) and not((A xor B) and C)",
               0b1<<14:"not(A and B) and (A xor B) and C",
               0b1<<15:"(A and B) and (A xor B) and C",#余剰出力
               0b1<<16:"not X",
               0b1<<17:"X",#結果の出力
               0b1<<18:"not G",
               0b1<<19:"G"#二段目の桁上げ出力
               }

logic_state_adder ={0b1:"not C",
                    0b1<<1:"C",
                    0b1<<2:"not B",
                    0b1<<3:"B",
                    0b1<<4:"not A",
                    0b1<<5:"A",#入力
                    0b1<<16:"not X",
                    0b1<<17:"X",#結果の出力
                    0b1<<18:"not G",
                    0b1<<19:"G"#二段目の桁上げ出力
                    }

#例えば初期状態は次のうちのどれか
initial =  [0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0000 <<6 | 0b010101,
            0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0000 <<6 | 0b011001,
            0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0000 <<6 | 0b100101,
            0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0000 <<6 | 0b101001]

#2桁目以降は18bitで表される
secondary =[0b0000 << 14 | 0b0000 << 10 | 0b00 << 8 | 0b0000 <<4 | 0b0101,
            0b0000 << 14 | 0b0000 << 10 | 0b00 << 8 | 0b0000 <<4 | 0b0110,
            0b0000 << 14 | 0b0000 << 10 | 0b00 << 8 | 0b0000 <<4 | 0b1001,
            0b0000 << 14 | 0b0000 << 10 | 0b00 << 8 | 0b0000 <<4 | 0b1010]

#終状態かどうか調べるにはX,notXのビットに結果が入っているか見ればよい
#次のビット列を状態とANDで作用させればよい
final =[0b0001 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0000 <<6 | 0b000000,
        0b0010 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0000 <<6 | 0b000000]

#最後の桁上げ出力を検出するのに必要
edge_final=[0b0101 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0000 <<6 | 0b000000,
            0b0110 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0000 <<6 | 0b000000,
            0b1001 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0000 <<6 | 0b000000,
            0b1010 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0000 <<6 | 0b000000]

#遷移はC-joinゲートの数だけある。今回は14個
#C-joinゲートによる遷移は次のビット列のXORで表現される
transition =   [0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0101 <<6 | 0b010100,#一段目
                0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0110 <<6 | 0b011000,#一段目
                0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0110 <<6 | 0b100100,#一段目
                0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b1001 <<6 | 0b101000,#一段目
                0b0001 << 16 | 0b0000 << 12 | 0b01 << 10 | 0b0001 <<6 | 0b000001,#二段目
                0b0010 << 16 | 0b0000 << 12 | 0b01 << 10 | 0b0010 <<6 | 0b000001,#二段目
                0b0010 << 16 | 0b0000 << 12 | 0b01 << 10 | 0b0001 <<6 | 0b000010,#二段目
                0b0001 << 16 | 0b0000 << 12 | 0b10 << 10 | 0b0010 <<6 | 0b000010,#二段目
                0b0100 << 16 | 0b0001 << 12 | 0b01 << 10 | 0b0100 <<6 | 0b000000,#三段目
                0b1000 << 16 | 0b0010 << 12 | 0b10 << 10 | 0b0100 <<6 | 0b000000,#三段目
                0b1000 << 16 | 0b0100 << 12 | 0b01 << 10 | 0b1000 <<6 | 0b000000,#三段目
                0b1000 << 16 | 0b1000 << 12 | 0b10 << 10 | 0b1000 <<6 | 0b000000]#三段目

#遷移が起こる状態を探索するための配列、配列内のオフセット数が同じものが対応する
#状態ビットとのANDで0にならないものの遷移が起こる
#本来は必要ないが前進確率と交代確率で遷移レートが違うと必要になる

forward =  [0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0000 <<6 | 0b010100,#一段目
            0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0000 <<6 | 0b011000,#一段目
            0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0000 <<6 | 0b100100,#一段目
            0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0000 <<6 | 0b101000,#一段目
            0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0001 <<6 | 0b000001,#二段目
            0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0010 <<6 | 0b000001,#二段目
            0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0001 <<6 | 0b000010,#二段目
            0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0010 <<6 | 0b000010,#二段目
            0b0000 << 16 | 0b0000 << 12 | 0b01 << 10 | 0b0100 <<6 | 0b000000,#三段目
            0b0000 << 16 | 0b0000 << 12 | 0b10 << 10 | 0b0100 <<6 | 0b000000,#三段目
            0b0000 << 16 | 0b0000 << 12 | 0b01 << 10 | 0b1000 <<6 | 0b000000,#三段目
            0b0000 << 16 | 0b0000 << 12 | 0b10 << 10 | 0b1000 <<6 | 0b000000]#三段目

backward = [0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0101 <<6 | 0b000000,#一段目
            0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0110 <<6 | 0b000000,#一段目
            0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b0110 <<6 | 0b000000,#一段目
            0b0000 << 16 | 0b0000 << 12 | 0b00 << 10 | 0b1001 <<6 | 0b000000,#一段目
            0b0001 << 16 | 0b0000 << 12 | 0b01 << 10 | 0b0000 <<6 | 0b000000,#二段目
            0b0010 << 16 | 0b0000 << 12 | 0b01 << 10 | 0b0000 <<6 | 0b000000,#二段目
            0b0010 << 16 | 0b0000 << 12 | 0b01 << 10 | 0b0000 <<6 | 0b000000,#二段目
            0b0001 << 16 | 0b0000 << 12 | 0b10 << 10 | 0b0000 <<6 | 0b000000,#二段目
            0b0100 << 16 | 0b0001 << 12 | 0b00 << 10 | 0b0000 <<6 | 0b000000,#三段目
            0b1000 << 16 | 0b0010 << 12 | 0b00 << 10 | 0b0000 <<6 | 0b000000,#三段目
            0b1000 << 16 | 0b0100 << 12 | 0b00 << 10 | 0b0000 <<6 | 0b000000,#三段目
            0b1000 << 16 | 0b1000 << 12 | 0b00 << 10 | 0b0000 <<6 | 0b000000]#三段目

#二桁目以降の遷移は遷移ビットの18bitを<<(16N) (N=1,2...)すればよい

node_pos = {"not C":[4,0],
            "C":[4,1],
            "not B":[0,3],
            "B":[0,4],
            "not A":[0,5],
            "A":[0,6],#入力
            transition[0]:[2,3],
            transition[1]:[2,4],
            transition[2]:[2,5],
            transition[3]:[2,6],
            "not(A xor B)":[4,2],
            "A xor B":[4,3],
            "A and B":[4,4],#X方向の一段目出力
            "not(A and B)":[4,5],
            "A and B":[4,6],#G方向の一段目出力
            transition[4]:[6,-1],
            transition[5]:[6,0],
            transition[6]:[6,1],
            transition[7]:[6,2],
            "not((A xor B) and C)":[8,3],
            "(A xor B) and C":[8,4],#桁上がりの移動1
            "not(A and B) and not((A xor B) and C)":[12,3],
            "(A and B) and not((A xor B) and C)":[12,4],
            "not(A and B) and (A xor B) and C":[12,5],
            "(A and B) and (A xor B) and C":[12,6],#桁上がりの移動
            transition[8]:[10,5],
            transition[9]:[10,6],
            transition[10]:[10,7],
            transition[11]:[10,8],
            "not X":[8,1],
            "X":[8,2],#結果の出力
            "not G":[12,7],
            "G":[12,8]#桁上げ出力
            }

wire_pos = {"not C":[4,0],
            "C":[4,1],
            "not B":[0,3],
            "B":[0,4],
            "not A":[0,5],
            "A":[0,6],#入力
            "not(A xor B)":[4,2],
            "A xor B":[4,3],
            "A and B":[4,4],#X方向の一段目出力
            "not(A and B)":[4,5],
            "A and B":[4,6],#G方向の一段目出力
            "not((A xor B) and C)":[8,3],
            "(A xor B) and C":[8,4],#桁上がりの移動1
            "not(A and B) and not((A xor B) and C)":[12,3],
            "(A and B) and not((A xor B) and C)":[12,4],
            "not(A and B) and (A xor B) and C":[12,5],
            "(A and B) and (A xor B) and C":[12,6],#桁上がりの移動
            "not X":[8,1],
            "X":[8,2],#結果の出力
            "not G":[12,7],
            "G":[12,8]#桁上げ出力
            }

gate_pos = {transition[0]:[2,3],
            transition[1]:[2,4],
            transition[2]:[2,5],
            transition[3]:[2,6],
            transition[4]:[6,-1],
            transition[5]:[6,0],
            transition[6]:[6,1],
            transition[7]:[6,2],
            transition[8]:[10,5],
            transition[9]:[10,6],
            transition[10]:[10,7],
            transition[11]:[10,8],
            }

def initial_test():
    print("one digit")
    for i in range(4):
        print("\ninitial state;"+str(bin(initial[i])))
        for j in range(Cjoin_num):
            if forward[j]&initial[i] == forward[j]:
                print("is transferred by "+str(bin(transition[j])))
                print("to next state;"+(bin(initial[i]^transition[j])))
    print("\ntwo digit")
    for i in range(4):
        for j in range(2):
            state = secondary[j] << Mod_length | initial[i]
            print("\ninitial state;"+str(bin(state)))
            for k in range(Cjoin_num):
                if forward[k]&state == forward[k]:
                    print("is transferred by 1st module gate;"+str(bin(transition[j])))
                    print("to next state;"+(bin(state^transition[j])))
            for t in range(Cjoin_num):
                if (forward[t]<<Base_length)&state == forward[t]<<Base_length:
                    print("is transferred by 2nd module gate;"+str(bin(transition[j])))
                    print("to next state;"+(bin(state^(transition[j]<<Base_length))))

def graph():
    G = nx.Graph()
    for i in range(len(logic_state)):
        G.add_node(logic_state[0b1<<i])
    for edge in transition:
        G.add_node(edge)
        for i in range(Mod_length):
            if edge & 0b1<<i:
                G.add_edge(edge,logic_state[0b1<<i])
    nx.draw(G,node_pos,with_labels=True,node_color='skyblue', edge_color='b',node_size=300)
    #nx.draw_networkx_nodes(G,node_pos,nodelist=["A","B","C"],node_color='red',node_size=400)
    plt.show()

if __name__ == "__main__":
    initial_test()
    graph()