import pandas as pd
import numpy as np

# 1. 엑셀 파일 직접 불러오기 (read_excel 사용)
# 만약 파일이 스크립트와 다른 폴더에 있다면 정확한 경로(예: r'E:\배지안폴더\...\토러스 접하는 조건.xlsx')를 입력해주세요.
file_path = '토러스 접하는 조건.xlsx' 
df = pd.read_excel(file_path)

def calculate_base_area(R, y, z, tx, ty):
    """신발끈 공식을 이용한 사각형 넓이 계산
    꼭짓점 순서: (R, 0) -> (-R, 0) -> (y, z) -> (T_2_x, T_2_y)
    """
    x_coords = [R, -R, y, tx]
    y_coords = [0, 0, z, ty]
    
    # 신발끈 공식: 0.5 * |(x0y1 - x1y0) + (x1y2 - x2y1) + (x2y3 - x3y2) + (x3y0 - x0y3)|
    area = 0.5 * abs(
        (x_coords[0]*y_coords[1] - x_coords[1]*y_coords[0]) +
        (x_coords[1]*y_coords[2] - x_coords[2]*y_coords[1]) +
        (x_coords[2]*y_coords[3] - x_coords[3]*y_coords[2]) +
        (x_coords[3]*y_coords[0] - x_coords[0]*y_coords[3])
    )
    return area

def compute_packing_density(row):
    """각 행(데이터)별 패킹 밀도 계산"""
    R, r, y, z, h = row['R'], row['r'], row['y'], row['z'], row['h']
    tx, ty = row['T_2_x'], row['T_2_y']
    
    # 밑면 넓이 및 셀 부피 계산
    area = calculate_base_area(R, y, z, tx, ty)
    v_cell = area * h
    
    # 토러스 1개의 부피: 💡 π^2 * R * r^2
    v_torus = (np.pi**2) * R * (r**2)
    
    # 패킹 밀도 계산 (0으로 나누기 방지 처리)
    if v_cell == 0:
        return np.nan
    return v_torus / v_cell

# 2. 패킹 밀도 계산 및 결과 열 추가
df['Packing_Density'] = df.apply(compute_packing_density, axis=1)

# 3. 콘솔 창에 결과 출력 (주요 지표 확인)
print("=== 종횡비(γ) 및 각도(θ)별 패킹 밀도 결과 ===")
print(df[['θ (deg)', 'γ', 'Packing_Density']].to_string(index=False))

# 4. 밀도 계산 결과가 포함된 새로운 파일로 저장하기
output_file = '토러스_밀도_계산_결과.xlsx'
df.to_excel(output_file, index=False)
print(f"\n계산 완료! 결과가 '{output_file}' 파일로 저장되었습니다.")
