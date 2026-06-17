import glob
import re
import os
import pandas as pd

def combine_min_error_rows():
    # 1. 현재 폴더에서 'torus(숫자).csv' 형태의 모든 파일 목록 가져오기
    file_list = glob.glob("torus(*.*).csv")
    
    if not file_list:
        print("[오류] 현재 디렉토리에 'torus(종횡비).csv' 파일이 존재하지 않습니다.")
        return

    # 파일 이름 정렬 (종횡비 숫자를 기준으로 오름차순 정렬)
    def extract_ratio(filename):
        match = re.search(r"torus\((.*?)\)\.csv", filename)
        return float(match.group(1)) if match else 0.0
    
    file_list.sort(key=extract_ratio)
    
    combined_results = []
    
    print(f"총 {len(file_list)}개의 CSV 파일에서 최소 오차 데이터를 탐색합니다.")
    print("-" * 60)
    
    # 2. 각 파일별로 순회하며 Absolute Error가 최소인 행 추출
    for file_path in file_list:
        try:
            # CSV 파일 읽기
            df = pd.read_csv(file_path)
            
            if df.empty or "Absolute Error" not in df.columns:
                print(f"  [스킵] {file_path}: 데이터가 비어있거나 'Absolute Error' 열이 없습니다.")
                continue
            
            # 'Absolute Error'가 최소값인 행 인덱스 찾기 (중복 최소값이 있을 경우 첫 번째 행 선택)
            min_idx = df["Absolute Error"].idxmin()
            min_error_row = df.loc[[min_idx]].copy()
            
            # 소스 파일 정보를 기록하기 위해 파일명 열 추가
            min_error_row.insert(0, "출처 파일", os.path.basename(file_path))
            
            # 결과 리스트에 누적
            combined_results.append(min_error_row)
            
            # 진행 상황 화면 출력
            current_min_err = df.loc[min_idx, "Absolute Error"]
            print(f"  [확인] {file_path:16s} -> 최소 오차: {current_min_err:.2e}")
            
        except Exception as e:
            print(f"  [에러] {file_path} 처리 중 오류 발생: {e}")
            
    # 3. 추출된 행들을 하나로 병합하여 저장
    if combined_results:
        final_df = pd.concat(combined_results, ignore_index=True)
        
        # 결과를 새 파일로 저장
        output_filename = "torus_min_error_summary.csv"
        final_df.to_csv(output_filename, index=False)
        
        print("-" * 60)
        print(f"[성공] 각 종횡비별 최적 패킹 데이터 통합 완료!")
        print(f"최종 시트가 '{output_filename}' 파일로 저장되었습니다. (총 {len(final_df)}행)")
        
        # 완성된 시트의 상위 데이터 일부 확인
        print("\n[통합 시트 미리보기]")
        print(final_df.head().to_string(index=False))
    else:
        print("[실패] 병합할 수 있는 유효한 데이터 행이 없습니다.")

if __name__ == "__main__":
    combine_min_error_rows()
