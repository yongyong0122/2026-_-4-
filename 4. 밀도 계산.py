import pandas as pd
import numpy as np

file_path = '토러스 접하는 조건.xlsx' 
df = pd.read_excel(file_path)

def calculate_base_area(R, y, z, tx, ty):
    """신발끈 공식을 이용한 사각형 넓이 계산
    꼭짓점 순서: (R, 0) -> (-R, 0) -> (y, z) -> (T_2_x, T_2_y)
    """
    x_coords = [R, -R, y, tx]
    y_coords = [0, 0, z, ty]
    
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
    
    area = calculate_base_area(R, y, z, tx, ty)
    v_cell = area * h

    v_torus = (np.pi**2) * R * (r**2)
    
    if v_cell == 0:
        return np.nan
    return v_torus / v_cell

df['Packing_Density'] = df.apply(compute_packing_density, axis=1)

print("=== 종횡비(γ) 및 각도(θ)별 패킹 밀도 결과 ===")
print(df[['θ (deg)', 'γ', 'Packing_Density']].to_string(index=False))

output_file = '토러스_밀도_계산_결과.xlsx'
df.to_excel(output_file, index=False)
print(f"\n계산 완료! 결과가 '{output_file}' 파일로 저장되었습니다.")
