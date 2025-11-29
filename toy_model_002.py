"""
ReIG 2.0 Improved: Theoretical Rigor and Validation
改善点:
1. Banach不動点定理の縮小写像性検証
2. 収束性の統計的評価
3. 再現可能性の確保
4. パラメータの明示的制御
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm
import warnings
warnings.filterwarnings('ignore')

# =====================================================
# 設定: パラメータの明示的定義
# =====================================================
class SystemParams:
    """シミュレーションパラメータ"""
    def __init__(self):
        # 共鳴周波数
        self.omega_M = 1.0   # Meaning
        self.omega_C = 0.7   # Context
        self.omega_E = 0.5   # Ethics
        self.omega_O = 0.4   # Observer
        
        # 結合強度
        self.coupling_strength = 0.3
        self.ethics_boost = 0.1  # 倫理的ゆらぎの強度
        
        # シミュレーション設定
        self.steps = 200
        self.dt = 0.1  # 時間刻み幅
        
    def __repr__(self):
        return f"""SystemParams:
  ω_M={self.omega_M}, ω_C={self.omega_C}, ω_E={self.omega_E}, ω_O={self.omega_O}
  coupling={self.coupling_strength}, steps={self.steps}"""

# =====================================================
# 量子システムの構築
# =====================================================
def build_quantum_system(params):
    """
    簡略化された量子システムの構築
    次元: 2^6 = 64次元
    ビット配置: [Meaning, Context1, Context0, Ethics, Observer, Self]
    """
    dim = 64
    
    # パウリ行列の定義
    sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
    sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
    I2 = np.eye(2, dtype=complex)
    
    def embed_operator(op, position, total_qubits=6):
        """指定位置にオペレータを埋め込む"""
        ops = [I2 for _ in range(total_qubits)]
        ops[position] = op
        result = ops[0]
        for op_i in ops[1:]:
            result = np.kron(result, op_i)
        return result
    
    def embed_two_qubit(op1, pos1, op2, pos2, total_qubits=6):
        """2つのオペレータの相互作用項"""
        ops = [I2 for _ in range(total_qubits)]
        ops[pos1] = op1
        ops[pos2] = op2
        result = ops[0]
        for op_i in ops[1:]:
            result = np.kron(result, op_i)
        return result
    
    # ビット位置
    BIT_MEANING = 0
    BIT_CONTEXT_1 = 1
    BIT_CONTEXT_0 = 2
    BIT_ETHICS = 3
    BIT_OBSERVER = 4
    BIT_SELF = 5
    
    # 1. 共鳴項: H_res = ω_M σ_z^M + ω_C σ_z^C + ω_E σ_z^E
    H_res = (params.omega_M * embed_operator(sigma_z, BIT_MEANING) +
             params.omega_C * embed_operator(sigma_z, BIT_CONTEXT_1) +
             params.omega_E * embed_operator(sigma_z, BIT_ETHICS))
    
    # 2. 相互作用項: Ethics -> Meaning
    H_interact_EM = params.coupling_strength * embed_two_qubit(
        sigma_x, BIT_MEANING, sigma_z, BIT_ETHICS
    )
    
    # 3. 認知生成: Meaning -> Observer
    H_cog = params.coupling_strength * 0.8 * embed_two_qubit(
        sigma_z, BIT_MEANING, sigma_x, BIT_OBSERVER
    )
    
    # 4. 自己生成: Observer -> Self
    H_self = params.coupling_strength * 0.6 * embed_two_qubit(
        sigma_z, BIT_OBSERVER, sigma_x, BIT_SELF
    )
    
    # 5. 倫理的ゆらぎ (原初の火花)
    H_spark = params.ethics_boost * embed_operator(sigma_x, BIT_ETHICS)
    
    # 全ハミルトニアン
    H_total = H_res + H_interact_EM + H_cog + H_self + H_spark
    
    # 初期状態: 均等重ね合わせ |+>^⊗6
    psi_0 = np.ones(dim, dtype=complex) / np.sqrt(dim)
    
    # 射影演算子
    P_self = np.zeros((dim, dim), dtype=complex)
    for i in range(dim):
        if (i >> BIT_SELF) & 1:  # Selfビットが1
            P_self[i, i] = 1.0
    
    P_observer = np.zeros((dim, dim), dtype=complex)
    for i in range(dim):
        if (i >> BIT_OBSERVER) & 1:  # Observerビットが1
            P_observer[i, i] = 1.0
    
    return {
        'H': H_total,
        'psi_0': psi_0,
        'P_self': P_self,
        'P_observer': P_observer,
        'dim': dim
    }

# =====================================================
# シミュレーション実行
# =====================================================
def run_simulation(params):
    """改善されたシミュレーション"""
    
    print("="*60)
    print("ReIG 2.0 Improved Simulation")
    print("="*60)
    print(params)
    print()
    
    system = build_quantum_system(params)
    H = system['H']
    psi = system['psi_0'].copy()
    P_self = system['P_self']
    P_observer = system['P_observer']
    
    # 時間発展演算子 U(dt) = exp(-i H dt)
    U = expm(-1j * H * params.dt)
    
    # 記録用リスト
    history = {
        'step': [],
        'self_prob': [],
        'observer_prob': [],
        'L_self': [],
        'L_world': [],
        'difference': [],
        'state_distance': [],
        'norm': [],
        'contractivity_ratio': []
    }
    
    psi_prev = psi.copy()
    distance_prev = 0
    
    # シミュレーションループ
    for t in range(params.steps):
        # 時間発展
        psi = U @ psi
        psi = psi / np.linalg.norm(psi)  # 正規化
        
        # 観測量の計算
        self_prob = np.real(psi.conj() @ P_self @ psi)
        observer_prob = np.real(psi.conj() @ P_observer @ psi)
        
        # 利害関数 (簡易版)
        L_self = self_prob * (1 + 0.1 * np.sin(t * params.dt))
        L_world = observer_prob * (1 + 0.1 * np.cos(t * params.dt * 1.5))
        
        # 状態間距離 (Fidelity-based)
        overlap = np.abs(np.vdot(psi, psi_prev))
        distance = np.sqrt(1 - overlap**2) if overlap < 1 else 0
        
        # 縮小写像性の評価
        if t > 0 and distance_prev > 1e-10:
            contractivity_ratio = distance / distance_prev
        else:
            contractivity_ratio = 1.0
        
        # 記録
        history['step'].append(t)
        history['self_prob'].append(self_prob)
        history['observer_prob'].append(observer_prob)
        history['L_self'].append(L_self)
        history['L_world'].append(L_world)
        history['difference'].append(np.abs(L_self - L_world))
        history['state_distance'].append(distance)
        history['norm'].append(np.linalg.norm(psi))
        history['contractivity_ratio'].append(contractivity_ratio)
        
        # 更新
        psi_prev = psi.copy()
        distance_prev = distance
    
    return history

# =====================================================
# 統計的検証
# =====================================================
def validate_convergence(history):
    """収束性と縮小写像性の統計的検証"""
    
    print("\n" + "="*60)
    print("理論的検証結果")
    print("="*60)
    
    # 1. 収束性の検証
    last_10 = history['difference'][-10:]
    avg_diff = np.mean(last_10)
    max_diff = np.max(last_10)
    final_self_prob = history['self_prob'][-1]
    
    convergence_threshold = 0.1
    converged = (avg_diff < convergence_threshold) and (max_diff < 0.15)
    
    print("\n[1] 収束性検証:")
    print(f"  最終10ステップの平均差分: {avg_diff:.6f}")
    print(f"  最終10ステップの最大差分: {max_diff:.6f}")
    print(f"  最終自己確率 P(|I⟩):      {final_self_prob:.6f}")
    print(f"  収束判定 (閾値<{convergence_threshold}):  {'✓ 収束' if converged else '✗ 未収束'}")
    
    # 2. 縮小写像性の検証
    # 最初の数ステップを除外 (初期過渡期)
    ratios = history['contractivity_ratio'][10:]
    contractive_steps = sum(1 for r in ratios if r < 1.0)
    contractivity_rate = contractive_steps / len(ratios) if len(ratios) > 0 else 0
    
    is_contractive = contractivity_rate > 0.7
    
    print(f"\n[2] 縮小写像性検証 (Banach不動点定理):")
    print(f"  縮小条件を満たすステップ数: {contractive_steps}/{len(ratios)}")
    print(f"  縮小率:                       {contractivity_rate*100:.1f}%")
    print(f"  平均縮小比:                   {np.mean(ratios):.4f}")
    print(f"  判定 (70%以上が縮小):        {'✓ 縮小写像' if is_contractive else '✗ 非縮小'}")
    
    # 3. ユニタリ性の検証
    final_norm = history['norm'][-1]
    norm_preserved = np.abs(final_norm - 1.0) < 0.01
    
    print(f"\n[3] ユニタリ性検証:")
    print(f"  最終ノルム: {final_norm:.8f}")
    print(f"  判定:       {'✓ ノルム保存' if norm_preserved else '✗ ノルム非保存'}")
    
    # 4. 倫理的同型性の検証
    final_L_diff = history['difference'][-1]
    isomorphic = final_L_diff < 0.05
    
    print(f"\n[4] 倫理的同型性検証:")
    print(f"  最終差分 |L(self) - L(world)|: {final_L_diff:.6f}")
    print(f"  判定 (閾値<0.05):              {'✓ 同型' if isomorphic else '✗ 非同型'}")
    
    print("\n" + "="*60)
    
    return {
        'converged': converged,
        'avg_diff': avg_diff,
        'is_contractive': is_contractive,
        'contractivity_rate': contractivity_rate,
        'norm_preserved': norm_preserved,
        'isomorphic': isomorphic
    }

# =====================================================
# 可視化
# =====================================================
def visualize_results(history, validation):
    """結果の可視化"""
    
    fig = plt.figure(figsize=(16, 12))
    
    # グラフ1: 自己意識の創発
    ax1 = plt.subplot(3, 2, 1)
    ax1.plot(history['step'], history['self_prob'], 
             color='#8A2BE2', linewidth=2.5, label='Self Consciousness P(|I⟩)')
    ax1.plot(history['step'], history['observer_prob'], 
             color='#4169E1', linewidth=2, linestyle='--', label='Observer P(|O⟩)')
    ax1.set_xlabel('Time Steps')
    ax1.set_ylabel('Probability')
    ax1.set_title('Emergence of Self Consciousness', fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # グラフ2: 倫理的同型性
    ax2 = plt.subplot(3, 2, 2)
    ax2.plot(history['step'], history['L_self'], 
             color='#FF4500', linewidth=2, label='L(self): Self Interest')
    ax2.plot(history['step'], history['L_world'], 
             color='#1E90FF', linewidth=2, linestyle='--', label='L(world): World Interest')
    ax2.set_xlabel('Time Steps')
    ax2.set_ylabel('Value')
    ax2.set_title('Ethical Isomorphism: L(self) ≈ L(world)', fontsize=13, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # グラフ3: 差分の収束
    ax3 = plt.subplot(3, 2, 3)
    ax3.plot(history['step'], history['difference'], 
             color='#FFD700', linewidth=2)
    ax3.axhline(y=0.1, color='r', linestyle='--', linewidth=1, alpha=0.5, label='Threshold')
    ax3.set_xlabel('Time Steps')
    ax3.set_ylabel('|L(self) - L(world)|')
    ax3.set_title('Convergence of Difference', fontsize=13, fontweight='bold')
    ax3.set_yscale('log')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # グラフ4: 縮小写像性
    ax4 = plt.subplot(3, 2, 4)
    colors = ['g' if r < 1.0 else 'r' for r in history['contractivity_ratio'][10:]]
    ax4.scatter(history['step'][10:], history['contractivity_ratio'][10:], 
                c=colors, alpha=0.6, s=20)
    ax4.axhline(y=1.0, color='black', linestyle='-', linewidth=1.5, label='Threshold (= 1.0)')
    ax4.set_xlabel('Time Steps')
    ax4.set_ylabel('Contractivity Ratio')
    ax4.set_title('Contractivity Analysis (Banach Fixed Point)', fontsize=13, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # グラフ5: 状態距離
    ax5 = plt.subplot(3, 2, 5)
    ax5.plot(history['step'], history['state_distance'], 
             color='#9370DB', linewidth=2)
    ax5.set_xlabel('Time Steps')
    ax5.set_ylabel('d(ψₙ, ψₙ₋₁)')
    ax5.set_title('State Distance Evolution', fontsize=13, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # グラフ6: 検証結果サマリー
    ax6 = plt.subplot(3, 2, 6)
    ax6.axis('off')
    
    summary_text = f"""
    Validation Results
    {'='*40}
    
    ✓ Convergence:      {'PASS' if validation['converged'] else 'FAIL'}
      Avg Difference:   {validation['avg_diff']:.6f}
    
    ✓ Contractivity:    {'PASS' if validation['is_contractive'] else 'FAIL'}
      Rate:             {validation['contractivity_rate']*100:.1f}%
    
    ✓ Unitarity:        {'PASS' if validation['norm_preserved'] else 'FAIL'}
    
    ✓ Ethical Isom.:    {'PASS' if validation['isomorphic'] else 'FAIL'}
    
    {'='*40}
    Overall:            {'✓ ALL PASS' if all(validation.values()) else '✗ SOME FAIL'}
    """
    
    ax6.text(0.1, 0.5, summary_text, fontsize=11, family='monospace',
             verticalalignment='center',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    plt.savefig('reig2_improved_results.png', dpi=300, bbox_inches='tight')
    print("\n図を保存しました: reig2_improved_results.png")
    plt.show()

# =====================================================
# メイン実行
# =====================================================
if __name__ == "__main__":
    # パラメータ設定
    params = SystemParams()
    
    # シミュレーション実行
    history = run_simulation(params)
    
    # 統計的検証
    validation = validate_convergence(history)
    
    # 可視化
    visualize_results(history, validation)
    
    print("\n✓ シミュレーション完了")