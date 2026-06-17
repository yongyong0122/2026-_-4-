import numpy as np
import pandas as pd

def get_min_distance(R, r, theta_rad, y, z, num_samples=200):
    """
    두 토러스의 중심 원 위에서 각각 num_samples 개의 점을 샘플링하여
    3차원 공간 상의 최단 거리를 구하는 최적화 함수 (Constraint 1)
    """
    alpha = np.linspace(0, 2 * np.pi, num_samples, endpoint=False)
    c1 = np.vstack([R * np.cos(alpha), R * np.sin(alpha), np.zeros_like(alpha)]).T
    
    beta = np.linspace(0, 2 * np.pi, num_samples, endpoint=False)
    c2 = np.vstack([
        R * np.cos(beta),
        y + R * np.sin(beta) * np.cos(theta_rad),
        z - R * np.sin(beta) * np.sin(theta_rad)
    ]).T
    
    dists = np.linalg.norm(c1[:, np.newaxis, :] - c2[np.newaxis, :, :], axis=2)
    return np.min(dists)

def binary_search_on_plane_condition(R, r, theta_rad, k, num_samples=200, tol=1e-7, max_iter=100):
    """
    z = tan(theta)*y + k 평면 위에서 최단 거리가 정확히 2r이 되는 
    외접 좌표 (y, z)를 이진 탐색으로 정밀 추적 (Constraint 2)
    """
    m = np.tan(theta_rad)
    
    # 해석적 해의 위치를 기반으로 안전한 이진 탐색 바운더리 설정
    inside_sqrt = r**2 - (R**2) * (np.sin(theta_rad / 2.0)**2)
    lhs = R * np.cos(theta_rad / 2.0) + np.sqrt(inside_sqrt)
    y_analytic = (np.cos(theta_rad) / np.cos(theta_rad / 2.0)) * (lhs - k * np.sin(theta_rad / 2.0))
    
    # 교점 주변 ±2.0 범위 지정
    low = y_analytic - 2.0
    high = y_analytic + 2.0
    
    # 양 끝점에서의 거리 경향 파악 (단조 증가 혹은 감소 대응)
    dist_low = get_min_distance(R, r, theta_rad, low, m * low + k, num_samples)
    dist_high = get_min_distance(R, r, theta_rad, high, m * high + k, num_samples)
    increasing = dist_high > dist_low
    
    for _ in range(max_iter):
        mid = (low + high) / 2.0
        y = mid
        z = m * y + k
        
        min_dist = get_min_distance(R, r, theta_rad, y, z, num_samples)
        
        if abs(min_dist - 2 * r) < tol:
            return y, z
            
        if increasing:
            if min_dist > 2 * r:
                high = mid
            else:
                low = mid
        else:
            if min_dist > 2 * r:
                low = mid
            else:
                high = mid
                
    mid = (low + high) / 2.0
    return mid, m * mid + k

def verify_torus_packing_fine_grained():
    # 주반지름 고정
    R = 10.0
    
    # 소반지름 r을 7.5부터 20.0까지 0.5씩 증가하는 배열 생성 (20.0을 포함하기 위해 20.1 설정)
    r_samples = np.arange(7.5, 20.1, 0.5)
    
    # 구간 세분화 설정
    num_theta_steps = 85   
    num_k_steps = 25      
    theta_degrees = np.linspace(0, 84, num_theta_steps)
    
    print(f"[설정] 기준 대반지름 R = {R}")
    print(f"소반지름 r을 7.5부터 20.0까지 0.5씩 증가시키며 연속 수치 분석을 진행합니다.")
    print(f"각 종횡비별로 개별 CSV 파일이 생성됩니다.\n")
    
    # 외각 루프: 소반지름 r 변경 및 종횡비(aspect_ratio) 계산
    for r in r_samples:
        aspect_ratio = r / R
        results = []
        
        print(f"-> 수치 분석 중: r = {r:.1f} (종횡비 γ = {aspect_ratio:.2f})")
        
        for deg in theta_degrees:
            theta_rad = np.radians(deg)
            
            # k의 최대 한계선 계산
            k_max = 2 * r * np.cos(theta_rad) + (2 * r * np.sin(theta_rad) + R) * np.tan(theta_rad)
            k_samples = np.linspace(0.0, k_max * 0.95, num_k_steps)
            
            for k in k_samples:
                inside_sqrt = r**2 - (R**2) * (np.sin(theta_rad / 2.0)**2)
                if inside_sqrt < 0:
                    continue
                    
                # 1. 제한된 평면 위에서 이진 탐색으로 수치해 (y, z) 도출
                y, z = binary_search_on_plane_condition(R, r, theta_rad, k)
                
                # 2. 수식의 좌변(LHS)과 우변(RHS) 산출
                lhs = R * np.cos(theta_rad / 2.0) + np.sqrt(inside_sqrt)
                phi_detected = np.arctan2(z, y)
                rhs = np.sqrt(y**2 + z**2) * np.cos(phi_detected - theta_rad / 2.0)
                
                abs_error = abs(lhs - rhs)
                
                results.append({
                    "γ (종횡비)": round(aspect_ratio, 4),
                    "R": R,
                    "r": r,
                    "θ (deg)": round(deg, 2),
                    "k 값": round(k, 3),
                    "y 좌표": round(y, 4),
                    "z 좌표": round(z, 4),
                    "LHS (수식 좌변)": round(lhs, 5),
                    "RHS (수식 우변)": round(rhs, 5),
                    "Absolute Error": abs_error
                })
                
        # 해당 r(종횡비)에 대한 데이터 연산이 끝난 후 개별 CSV 파일로 즉시 저장
        if results:
            df = pd.DataFrame(results)
            # 파일명 형식: torus(종횡비 값).csv (예: torus(0.75).csv, torus(1.00).csv 등)
            csv_filename = f"종횡비별 자료//torus({aspect_ratio:.2f}).csv"
            df.to_csv(csv_filename, index=False)
            
            min_err = df["Absolute Error"].min()
            print(f"   [완료] 파일 저장됨: '{csv_filename}' (데이터: {len(df)}개, 최소 오차: {min_err:.2e})")
            
    print("\n==================================================")
    print("   모든 종횡비 구간에 대한 전수 수치 분석이 완료되었습니다.  ")
    print("==================================================")

if __name__ == "__main__":
    verify_torus_packing_fine_grained()
