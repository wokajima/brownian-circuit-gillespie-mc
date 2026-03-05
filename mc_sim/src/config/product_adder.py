import networkx as nx
import matplotlib.pyplot as plt

#積項加算器を定義する変数
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
#AandB,Aand notB,notA and B,notA and notB
#AandB,Aand notB,notA and B,notA and notB(同じ論理変数だが違うワイヤーがそれぞれ二つある)
#二段目出力
#G,notG,X,notX
#全てで18bitの変数になる
#0bG,notG,X,notX,AandB,Aand notB,notA and B,notA and notB,AandB,Aand notB,notA and B,notA and notB,A,notA,B,notB,C,notC
#GとCが先頭と最後尾にきていて桁上げが自然に実装されている
#二桁目以降はCを除いた16bitを<<(16N+2) (N=1,2...)して結合すればよい
# S_N << 16N-14 | S_(N-1) << 16N-30 | ... | S_2 << 16+2 | S_1

Mod_length = 18     #モジュール全体の状態数
Base_length = 16    #桁上がり/桁上げを除いた状態数
Cjoin_num = 12      #C-joinゲートの数

#0bG,notG,X,notX,AandB,Aand notB,notA and B,notA and notB,AandB,Aand notB,notA and B,notA and notB,A,notA,B,notB,C,notC
logic_state = {0b1:"not C",
               0b1<<1:"C",
               0b1<<2:"not B",
               0b1<<3:"B",
               0b1<<4:"not A",
               0b1<<5:"A",
               0b1<<6:"not A and not B",
               0b1<<7:"not A and B",
               0b1<<8:"A and not B",
               0b1<<9:"A and B",
               0b1<<10:"not A and not B-X",
               0b1<<11:"not A and B-X",
               0b1<<12:"A and not B-X",
               0b1<<13:"A and B-X",
               0b1<<14:"not X",
               0b1<<15:"X",
               0b1<<16:"not G",
               0b1<<17:"G"
               }
logic_state_adder ={0b1:"not C",
                    0b1<<1:"C",
                    0b1<<2:"not B",
                    0b1<<3:"B",
                    0b1<<4:"not A",
                    0b1<<5:"A",
                    0b1<<14:"not X",
                    0b1<<15:"X",
                    0b1<<16:"not G",
                    0b1<<17:"G"
                    }

#例えば初期状態は次のうちのどれか
initial =  [0b0000 << 14 | 0b0000 << 10 | 0b0000 <<6 | 0b010101,
            0b0000 << 14 | 0b0000 << 10 | 0b0000 <<6 | 0b011001,
            0b0000 << 14 | 0b0000 << 10 | 0b0000 <<6 | 0b100101,
            0b0000 << 14 | 0b0000 << 10 | 0b0000 <<6 | 0b101001]

secondary =[0b0000 << 12 | 0b0000 << 8 | 0b0000 <<4 | 0b0101,
            0b0000 << 12 | 0b0000 << 8 | 0b0000 <<4 | 0b0110,
            0b0000 << 12 | 0b0000 << 8 | 0b0000 <<4 | 0b1001,
            0b0000 << 12 | 0b0000 << 8 | 0b0000 <<4 | 0b1010]

#終状態かどうか調べるにはX,notXのビットに結果が入っているか見ればよい
#次のビット列を状態とANDで作用させればよい
final =[0b0001 << 14 | 0b0000 << 10 | 0b0000 <<6 | 0b000000,
        0b0010 << 14 | 0b0000 << 10 | 0b0000 <<6 | 0b000000,]

#遷移はC-joinゲートの数だけある。今回は12個
#C-joinゲートによる遷移は次のビット列のXORで表現される
transition =   [0b0000 << 14 | 0b0001 << 10 | 0b0001 <<6 | 0b010100,
                0b0000 << 14 | 0b0010 << 10 | 0b0010 <<6 | 0b011000,
                0b0000 << 14 | 0b0100 << 10 | 0b0100 <<6 | 0b100100,
                0b0000 << 14 | 0b1000 << 10 | 0b1000 <<6 | 0b101000,
                0b0101 << 14 | 0b0001 << 10 | 0b0000 <<6 | 0b000001,
                0b0110 << 14 | 0b0001 << 10 | 0b0000 <<6 | 0b000010,
                0b0110 << 14 | 0b0010 << 10 | 0b0000 <<6 | 0b000001,
                0b1001 << 14 | 0b0010 << 10 | 0b0000 <<6 | 0b000010,
                0b0110 << 14 | 0b0100 << 10 | 0b0000 <<6 | 0b000001,
                0b1001 << 14 | 0b0100 << 10 | 0b0000 <<6 | 0b000010,
                0b1001 << 14 | 0b1000 << 10 | 0b0000 <<6 | 0b000001,
                0b1010 << 14 | 0b1000 << 10 | 0b0000 <<6 | 0b000010]

#遷移が起こる状態を探索するための配列、配列内のオフセット数が同じものが対応する
#状態ビットとのANDで0にならないものの遷移が起こる
#本来は必要ないが前進確率と交代確率で遷移レートが違うと必要になる

forward =  [0b0000 << 14 | 0b0000 << 10 | 0b0000 <<6 | 0b010100,
            0b0000 << 14 | 0b0000 << 10 | 0b0000 <<6 | 0b011000,
            0b0000 << 14 | 0b0000 << 10 | 0b0000 <<6 | 0b100100,
            0b0000 << 14 | 0b0000 << 10 | 0b0000 <<6 | 0b101000,
            0b0000 << 14 | 0b0001 << 10 | 0b0000 <<6 | 0b000001,
            0b0000 << 14 | 0b0001 << 10 | 0b0000 <<6 | 0b000010,
            0b0000 << 14 | 0b0010 << 10 | 0b0000 <<6 | 0b000001,
            0b0000 << 14 | 0b0010 << 10 | 0b0000 <<6 | 0b000010,
            0b0000 << 14 | 0b0100 << 10 | 0b0000 <<6 | 0b000001,
            0b0000 << 14 | 0b0100 << 10 | 0b0000 <<6 | 0b000010,
            0b0000 << 14 | 0b1000 << 10 | 0b0000 <<6 | 0b000001,
            0b0000 << 14 | 0b1000 << 10 | 0b0000 <<6 | 0b000010]

backward = [0b0000 << 14 | 0b0001 << 10 | 0b0001 <<6 | 0b000000,
            0b0000 << 14 | 0b0010 << 10 | 0b0010 <<6 | 0b000000,
            0b0000 << 14 | 0b0100 << 10 | 0b0100 <<6 | 0b000000,
            0b0000 << 14 | 0b1000 << 10 | 0b1000 <<6 | 0b000000,
            0b0101 << 14 | 0b0000 << 10 | 0b0000 <<6 | 0b000000,
            0b0110 << 14 | 0b0000 << 10 | 0b0000 <<6 | 0b000000,
            0b0110 << 14 | 0b0000 << 10 | 0b0000 <<6 | 0b000000,
            0b1001 << 14 | 0b0000 << 10 | 0b0000 <<6 | 0b000000,
            0b0110 << 14 | 0b0000 << 10 | 0b0000 <<6 | 0b000000,
            0b1001 << 14 | 0b0000 << 10 | 0b0000 <<6 | 0b000000,
            0b1001 << 14 | 0b0000 << 10 | 0b0000 <<6 | 0b000000,
            0b1010 << 14 | 0b0000 << 10 | 0b0000 <<6 | 0b000000]

#二桁目以降の遷移は遷移ビットの18bitを<<(16N) (N=1,2...)すればよい

#グラフ描画のためのノードの設定
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
            "not A and not B":[3,7],
            "not A and B":[3,8],
            "A and not B":[3,9],
            "A and B":[3,10],
            transition[4]:[6,0],
            transition[5]:[6,1],
            transition[6]:[6,2],
            transition[7]:[6,3],
            transition[8]:[6,4],
            transition[9]:[6,5],
            transition[10]:[6,6],
            transition[11]:[6,7],
            "not A and not B-X":[4,3],
            "not A and B-X":[4,4],
            "A and not B-X":[4,5],
            "A and B-X":[4,6],
            "not X":[8,2],
            "X":[8,3],#結果の出力
            "not G":[8,5],
            "G":[8,6]#桁上げ出力
            }
wire_pos = {"not C":[4,0],
            "C":[4,1],
            "not B":[0,3],
            "B":[0,4],
            "not A":[0,5],
            "A":[0,6],#入力
            "not A and not B":[3,7],
            "not A and B":[3,8],
            "A and not B":[3,9],
            "A and B":[3,10],
            "not A and not B-X":[4,3],
            "not A and B-X":[4,4],
            "A and not B-X":[4,5],
            "A and B-X":[4,6],
            "not X":[8,2],
            "X":[8,3],#結果の出力
            "not G":[8,5],
            "G":[8,6]#桁上げ出力
            }
gate_pos = {transition[0]:[2,3],
            transition[1]:[2,4],
            transition[2]:[2,5],
            transition[3]:[2,6],
            transition[4]:[6,0],
            transition[5]:[6,1],
            transition[6]:[6,2],
            transition[7]:[6,3],
            transition[8]:[6,4],
            transition[9]:[6,5],
            transition[10]:[6,6],
            transition[11]:[6,7],
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
        for j in range(4):
            state = secondary[j] << 18 | initial[i]
            print("\ninitial state;"+str(bin(state)))
            for k in range(Cjoin_num):
                if forward[k]&state == forward[k]:
                    print("is transferred by 1st module gate;"+str(bin(transition[j])))
                    print("to next state;"+(bin(state^transition[j])))
            for t in range(Cjoin_num):
                if (forward[t]<<16)&state == forward[t]<<16:
                    print("is transferred by 2nd module gate;"+str(bin(transition[j])))
                    print("to next state;"+(bin(state^(transition[j]<<16))))

if __name__ == "__main__":
    G = nx.Graph()
    for i in range(len(logic_state)):
        G.add_node(logic_state[0b1<<i])
    for edge in transition:
        G.add_node(edge)
        for i in range(Mod_length):
            if edge & 0b1<<i:
                G.add_edge(edge,logic_state[0b1<<i])
    nx.draw(G,node_pos,with_labels=True,node_color='skyblue', edge_color='b',node_size=300)
    nx.draw_networkx_nodes(G,node_pos,gate_pos,node_color='gray',node_size=400)
    nx.draw_networkx_nodes(G,node_pos,nodelist=["A","B","C"],node_color='red',node_size=400)
    plt.show()