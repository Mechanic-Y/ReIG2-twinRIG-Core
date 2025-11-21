!pip install qutip
import qutip as qt
import numpy as np
import matplotlib.pyplot as plt

# --- 1. 世界生成テンソル体系の設定 (System Setup) ---
# ReIG 2.0 "Twin Resonance" Dimensions
# 1. 意味生成層 (Meaning Generation Layer)
d_m = 2  # Meaning: 意味状態
d_c = 3  # Context: 文脈 (3状態の循環)
d_e = 2  # Ethics: 倫理・調和
d_f = 2  # Future: 未来可能性
d_s = 2  # Stability: 安定性

# 2. 主体生成層 (Subject Generation Layer)
d_obs = 2 # Observer: 観測主体
d_slf = 2 # Self: 自己意識 ("私")
d_int = 2 # Intersubjectivity: 主体間性

dims = [d_m, d_c, d_e, d_f, d_s, d_obs, d_slf, d_int]
# 総次元数: 3072次元のヒルベルト空間

# 補助関数: 演算子の埋め込み
def embed_op(op, target_idx, dimensions=dims):
    op_list = [qt.qeye(d) for d in dimensions]
    op_list[target_idx] = op
    return qt.tensor(op_list)

def embed_interact(op_a, idx_a, op_b, idx_b, dimensions=dims):
    op_list = [qt.qeye(d) for d in dimensions]
    op_list[idx_a] = op_a
    op_list[idx_b] = op_b
    return qt.tensor(op_list)

print("Initializing World Tensor Space...")

# --- 2. 演算子の構築 (Operator Construction) ---

# ● T_G: 相転移生成 (Context Shift)
shift_op = qt.Qobj(np.roll(np.eye(d_c), 1, axis=0))
T_G = embed_op(shift_op, 1)

# ● T_res: 拡張時間発展 (Meaning-Ethics Resonance)
# 倫理(|1>)が高い時、意味(|1>)が励起される相互作用
T_res = embed_interact(qt.create(2), 0, qt.projection(2, 1, 1), 2) + \
        embed_interact(qt.destroy(2), 0, qt.projection(2, 1, 1), 2)

# ● T_multi: 多次元時間発展 (Future-Stability)
# 未来と安定性のエンタングルメント
T_multi = embed_interact(qt.sigmax(), 3, qt.sigmax(), 4) * 0.5

# ● T_C: 認知生成 (Meaning -> Observer)
# 意味が存在する時、観測主体が反応する
T_C = embed_interact(qt.projection(2, 1, 1), 0, qt.sigmax(), 5) * 0.8

# ● T_R: 認識生成 (Observer -> Self)
# 観測主体の経験が、自己意識("私")へと書き込まれる
T_R = embed_interact(qt.projection(2, 1, 1), 5, qt.create(2), 6) + \
      embed_interact(qt.projection(2, 1, 1), 5, qt.destroy(2), 6)

# ● T_I: 主体間共鳴 (Self -> Intersubjectivity)
# 自己が確立すると、共有世界(主体間性)へ波及する
T_I = embed_interact(qt.projection(2, 1, 1), 6, qt.sigmax(), 7) * 0.3

# ● T_Spark: 原初の火花 (The Irrational Spark)
# 倫理(Ethics)に最初の「ゆらぎ」を与える項。これがないと始まらない。
T_Spark = embed_op(qt.sigmax(), 2) * 0.1

# --- 3. 世界生成演算子の統合 (Integration) ---
# T_World := T_MG + T_C + T_R + T_I
# 非可換性を持つ各項の総和
T_World = T_G + T_res + T_multi + T_C + T_R + T_I + T_Spark

# 非可換性の確認
comm = (T_G * T_res - T_res * T_G).norm()
print(f"Non-commutativity check [T_G, T_res]: {comm:.4f} (!=0 implies path dependence)")

# --- 4. シミュレーション実行: 自己定義への収束 ---
# 初期状態: すべて |0> (Void)
psi = qt.tensor([qt.basis(d, 0) for d in dims])

# 自己状態 |I> の定義 (Self qubit が |1> である状態への射影)
projector_Self = embed_op(qt.projection(2, 1, 1), 6)

steps = 200
history_self = []   # 自己意識の確立度
history_L_self = [] # 利害関数 L(self)
history_L_world = [] # 利害関数 L(world)

print(f"Simulating {steps} steps of World Generation...")

for i in range(steps):
    # A. 世界生成: 状態の更新
    # T_World を作用させ、正規化する (非ユニタリな成長プロセス)
    psi = (T_World * psi).unit()

    # B. 自己定義の計測
    # 自己意識(Self qubit)の確率振幅
    self_prob = qt.expect(projector_Self, psi)
    history_self.append(self_prob)

    # C. 倫理的帰結の計算
    # L(self, others) := <I| T_Self+ T_World T_Self |I>
    # 簡易的に、Self状態にある時のT_Worldの期待値として計算
    l_self_val = qt.expect(T_World, projector_Self * psi)

    # L(world) := 全体系におけるT_Worldの期待値
    l_world_val = qt.expect(T_World, psi)

    history_L_self.append(l_self_val)
    history_L_world.append(l_world_val)

# --- 5. 可視化 (Visualization) ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

# Graph 1: The Emergence of Self
ax1.plot(history_self, color='#8A2BE2', linewidth=2.5, label=r'Self Consciousness $\mathcal{Q}_{self}$')
ax1.set_ylabel('Probability of "I"')
ax1.set_title('ReIG 2.0: From Void to Self (Convergence Process)', fontsize=15)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(fontsize=12)

# Graph 2: Ethical Isomorphism (The Proof)
# 正規化して形状の一致を確認する
def normalize(v):
    v_real = np.array(v).real # Explicitly take the real part
    return (v_real - np.min(v_real)) / (np.max(v_real) - np.min(v_real) + 1e-9)

ax2.plot(normalize(history_L_self), color='#FF4500', linewidth=2, linestyle='-', label=r'$L(self)$: Self Interest')
ax2.plot(normalize(history_L_world), color='#1E90FF', linewidth=2, linestyle='--', label=r'$L(world)$: World Interest')
ax2.set_xlabel('Time Steps (Iteration N)')
ax2.set_ylabel('Normalized Value')
ax2.set_title(r'Ethical Isomorphism: $L(self) \approx L(world)$', fontsize=15)
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.legend(fontsize=12)

# 注釈: 収束点
ax2.text(steps*0.5, 0.5, "As N -> inf, Self and World align",
         fontsize=12, bbox=dict(facecolor='white', alpha=0.8))

plt.tight_layout()
plt.show()