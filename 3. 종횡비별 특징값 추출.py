import glob
import re
import os
import pandas as pd

def combine_min_error_rows():
    file_list = glob.glob("torus(*.*).csv")
    if not file_list:
        print("[오류] 현재 디렉토리에 'torus(종횡비).csv' 파일이 존재하지 않습니다.")
        return

    def extract_ratio(filename):
        match = re.search(r"torus\((.*?)\)\.csv", filename)
        return float(match.group(1)) if match else 0.0
    
    file_list.sort(key=extract_ratio)
    combined_results = []
    print(f"총 {len(file_list)}개의 CSV 파일에서 최소 오차 데이터를 탐색합니다.")
    print("-" * 60)
    
    for file_path in file_list:
        try:
            # CSV 파일 읽기
            df = pd.read_csv(file_path)
            
            if df.empty or "Absolute Error" not in df.columns:
                print(f"  [스킵] {file_path}: 데이터가 비어있거나 'Absolute Error' 열이 없습니다.")
                continue

            min_idx = df["Absolute Error"].idxmin()
            min_error_row = df.loc[[min_idx]].copy()

            min_error_row.insert(0, "출처 파일", os.path.basename(file_path))

            combined_results.append(min_error_row)

            current_min_err = df.loc[min_idx, "Absolute Error"]
            print(f"  [확인] {file_path:16s} -> 최소 오차: {current_min_err:.2e}")
            
        except Exception as e:
            print(f"  [에러] {file_path} 처리 중 오류 발생: {e}")

    if combined_results:
        final_df = pd.concat(combined_results, ignore_index=True)

        output_filename = "torus_min_error_summary.csv"
        final_df.to_csv(output_filename, index=False)
        
        print("-" * 60)
        print(f"[성공] 각 종횡비별 최적 패킹 데이터 통합 완료!")
        print(f"최종 시트가 '{output_filename}' 파일로 저장되었습니다. (총 {len(final_df)}행)")

        print("\n[통합 시트 미리보기]")
        print(final_df.head().to_string(index=False))
    else:
        print("[실패] 병합할 수 있는 유효한 데이터 행이 없습니다.")

if __name__ == "__main__":
    combine_min_error_rows()
