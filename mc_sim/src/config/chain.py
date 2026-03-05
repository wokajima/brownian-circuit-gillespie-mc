import networkx as nx
import matplotlib.pyplot as plt

#一次元鎖を定義する変数
#遷移と状態を定義している

#実のところ積項で入力状態を完全に保存する積和標準形回路のシミュレーションになっている。
#このモジュール一つあたりでC-joinゲートは一段(四個)なので入力変数は二個
#モジュール二つで二段(4+8個)、入力変数は三個
#つまりN個のモジュールでN段、入力変数がN+1の回路になる。
#この時のC-joinゲートの数は2^2+2^3+2^4+ ... + 2^(N+1)個になる

#N入力で一つの変数だけ次のモジュールに渡す回路の直列も一次元鎖と見做せる
#つまり、情報を完全に保存しながら進行する回路は全て一次元鎖と見做せる

#状態はワイヤーに対応した1bitを複数桁用意した状態変数で記述される
#粒子がある場合1,ない場合0となる
#例えば0~4のワイヤーのうちワイヤー0と2にある状態は、0b00101、で表される

#遷移は1の場所を移す論理演算で記述される
#例えば0と2のトークンを4と5に移すとき、XOR0b11101を作用させる
#生成消滅演算子を作用させていると考えられる

#論理変数はA=1,B=1のみ

#全てのワイヤーは次のようになる
#入力
#A,B(=1,1)
#出力
#A and B
#A and B
#全てで4bitの変数になる
#二桁目以降は3bitを<<(2N+2) (N=1,2...)して結合すればよい
# S_N << 2N+2 | S_(N-1) << 2N-2 | ... | S_2 << 4 | S_1

Mod_length = 4     #モジュール全体の状態数
Base_length = 3    #桁上げを除いた状態数
Cjoin_num = 1      #C-joinゲートの数

#0bG,notG,X,notX,C^2,not C^2,C^1,not C^1,A vor B,not(A xor B),A and B,A xor B,not A and not B,A,notA,B,notB,C,notC
logic_state = {0b1:"B",
               0b1<<1:"A",
               0b1<<2:"A and B",
               0b1<<3:"A and B-X"
               }

#例えば初期状態は次のうちのどれか
initial =  [0b0011]

#2桁目以降は4bitで表される
secondary =[0b001]

#終状態かどうか調べるには最後のビットに結果が入っているか見ればよい
#次のビット列を状態とANDで作用させればよい
final =[0b1100,
        0b0100]

#遷移はC-joinゲートの数だけある。今回は1個
#C-joinゲートによる遷移は次のビット列のXORで表現される
transition =  [0b1111]

#遷移が起こる状態を探索するための配列、配列内のオフセット数が同じものが対応する
#状態ビットとのANDで0にならないものの遷移が起こる
#本来は必要ないが前進確率と交代確率で遷移レートが違うと必要になる

forward =  [0b0011]

backward = [0b1100]

#二桁目以降の遷移は遷移ビットの18bitを<<(16N) (N=1,2...)すればよい

node_pos = {"B":(0,0),
            "A":(0,1),
            "A and B":(2,0),
            "A and B-X":(2,1),
            transition[0]:(1,0.5)
            }

def initial_test():
    print("one digit")
    for i in range(1):
        print("\ninitial state;"+str(bin(initial[i])))
        for j in range(Cjoin_num):
            if forward[j]&initial[i] == forward[j]:
                print("is transferred by "+str(bin(transition[j])))
                print("to next state;"+(bin(initial[i]^transition[j])))
    print("\ntwo digit")
    for i in range(1):
        for j in range(1):
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