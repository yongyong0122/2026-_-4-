import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_torus_contact_final(R, r, theta_deg, k, y_val, z_val):
    """
    두 번째 원(빨간색)이 z = tan(theta)*y + k 평면의 기울기 방향과 
    완벽히 일치하도록 회전 방향을 정방향(+theta)으로 수정하여 시각화합니다.
    """
    theta_rad = np.radians(theta_deg)
    
    fig = plt.figure(figsize=(11, 9))
    ax = fig.add_subplot(111, projection='3d')
    
    # 1. Torus 1 중심 원 생성 (xy 평면, 파란색)
    alpha = np.linspace(0, 2 * np.pi, 200)
    c1_x = R * np.cos(alpha)
    c1_y = R * np.sin(alpha)
    c1_z = np.zeros_like(alpha)
    ax.plot(c1_x, c1_y, c1_z, color='blue', linewidth=2.5, label='Torus 1 Center Circle')
    
    # 2. Torus 2 중심 원 생성 (기울기 방향을 +theta_rad로 수정)
    beta = np.linspace(0, 2 * np.pi, 200)
    x_local = R * np.cos(beta)
    y_local = R * np.sin(beta)
    z_local = np.zeros_like(beta)
    
    # x축 기준 정방향(+theta) 회전 변환 적용
    c2_x = x_local
    c2_y = y_val + y_local * np.cos(theta_rad) - z_local * np.sin(theta_rad)
    c2_z = z_val + y_local * np.sin(theta_rad) + z_local * np.cos(theta_rad)
    
    ax.plot(c2_x, c2_y, c2_z, color='red', linewidth=2.5, label='Torus 2 Center Circle (Aligned)')
    
    # 3. 제약 평면 시각화 (원들이 포함되도록 바운더리 설정)
    x_grid = np.linspace(-R-r, R+r, 10)
    y_grid = np.linspace(y_val - R - 5, y_val + R + 5, 10)
    X_plane, Y_plane = np.meshgrid(x_grid, y_grid)
    Z_plane = np.tan(theta_rad) * Y_plane + k
    
    # 평면 그리기 (초록색 투명 평면)
    ax.plot_surface(X_plane, Y_plane, Z_plane, color='green', alpha=0.2, shade=False, label='Constraint Plane')
    
    # 4. 두 원 사이의 최단 거리 계산 및 표시
    c1 = np.vstack([c1_x, c1_y, c1_z]).T
    c2 = np.vstack([c2_x, c2_y, c2_z]).T
    dists = np.linalg.norm(c1[:, np.newaxis, :] - c2[np.newaxis, :, :], axis=2)
    idx1, idx2 = np.unravel_index(np.argmin(dists), dists.shape)
    
    pt1 = c1[idx1]
    pt2 = c2[idx2]
    
    # 최단 거리 선분 표시 (검은색 점선, 이 길이가 2r=16이 됨)
    ax.plot([pt1[0], pt2[0]], [pt1[1], pt2[1]], [pt1[2], pt2[2]], 
            color='black', linestyle='--', linewidth=2, marker='o', 
            label=f'Min Distance Line (Length = {dists[idx1, idx2]:.2f})')
    
    # 5. 중심점 및 원점 마커 표시
    ax.scatter([0], [y_val], [z_val], color='purple', s=60, zorder=5, label=f'Torus 2 Center (0, {y_val:.2f}, {z_val:.2f})')
    ax.scatter([0], [0], [0], color='black', s=30, label='Origin (0,0,0)')
    
    # 6. 그래프 포맷 설정
    ax.set_title(f"Torus Packing: Corrected Rotation ($\theta$ = {theta_deg}°, $k$ = {k})", fontsize=13)
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    
    # 축 왜곡 방지 균등화 비율 설정
    all_x = np.concatenate([c1_x, c2_x])
    all_y = np.concatenate([c1_y, c2_y])
    all_z = np.concatenate([c1_z, c2_z])
    
    max_range = np.array([all_x.max()-all_x.min(), all_y.max()-all_y.min(), all_z.max()-all_z.min()]).max() / 2.0
    mid_x = (all_x.max()+all_x.min()) * 0.5
    mid_y = (all_y.max()+all_y.min()) * 0.5
    mid_z = (all_z.max()+all_z.min()) * 0.5
    
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    ax.legend(loc='upper left')
    plt.show()
# ==========================================================
# [실행 영역] 질문자님의 데이터 세트를 대입하여 확인해 보세요.
# ==========================================================
if __name__ == "__main__":
    R_val = 10.0
    r_val = 10.0
    
    # 예시: 세타가 30도이고 k 평면 위에 있을 때의 배치 데이터 입력
    # (본인의 전수검사 출력 테이블에서 한 줄을 골라 매칭해 보세요)
    plot_torus_contact_final(R=R_val, r=r_val, theta_deg=59, k=22.19, y_val=3.8185, z_val=28.5451)
