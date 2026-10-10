import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def find_column(df, attr_query):
    attr_clean = attr_query.strip().lower()
    for col in df.columns:
        if col.strip().lower() == attr_clean:
            return col
    for col in df.columns:
        col_clean = col.strip().lower()
        if col_clean.endswith("_" + attr_clean) or col_clean == attr_clean:
            return col
    for col in df.columns:
        if attr_clean in col.strip().lower():
            return col
    return None

def plot_radar(df, p1_name, p2_name, attributes):
    row1 = df[df["Player"].str.contains(p1_name, case=False, na=False)]
    row2 = df[df["Player"].str.contains(p2_name, case=False, na=False)]

    if row1.empty:
        print(f"Lỗi: Không tìm thấy cầu thủ '{p1_name}'!")
        return
    if row2.empty:
        print(f"Lỗi: Không tìm thấy cầu thủ '{p2_name}'!")
        return

    player1 = row1.iloc[0]["Player"]
    player2 = row2.iloc[0]["Player"]

    valid_cols = []
    labels = []
    for attr in attributes:
        matched = find_column(df, attr)
        if matched:
            valid_cols.append(matched)
            short_label = matched.split("_")[-1] if "_" in matched else matched
            labels.append(short_label)
        else:
            print(f"Cảnh báo: Không tìm thấy thuộc tính nào tương ứng với '{attr}'!")

    if len(valid_cols) < 3:
        print("Lỗi: Cần tối thiểu 3 thuộc tính hợp lệ để vẽ biểu đồ Radar!")
        return

    vals1 = []
    vals2 = []
    raw1_info = []
    raw2_info = []

    for col in valid_cols:
        all_vals = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce").fillna(0)
        max_val = all_vals.max() if all_vals.max() > 0 else 1.0

        v1 = pd.to_numeric(str(row1.iloc[0][col]).replace(",", ""), errors="coerce")
        v2 = pd.to_numeric(str(row2.iloc[0][col]).replace(",", ""), errors="coerce")
        v1 = 0.0 if pd.isna(v1) else float(v1)
        v2 = 0.0 if pd.isna(v2) else float(v2)

        raw1_info.append(f"{v1:.0f}")
        raw2_info.append(f"{v2:.0f}")

        vals1.append((v1 / max_val) * 100)
        vals2.append((v2 / max_val) * 100)

    num_vars = len(valid_cols)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    vals1 += vals1[:1]
    vals2 += vals2[:1]
    angles += angles[:1]

    display_labels = [f"{lbl}\n({r1} vs {r2})" for lbl, r1, r2 in zip(labels, raw1_info, raw2_info)]

    # 1. Tạo figure với kích thước chuẩn
    fig, ax = plt.subplots(figsize=(8.5, 8.5), subplot_kw=dict(polar=True))

    # 2. Vẽ 2 cầu thủ
    ax.plot(angles, vals1, color='#1f77b4', linewidth=2.5, label=player1)
    ax.fill(angles, vals1, color='#1f77b4', alpha=0.25)

    ax.plot(angles, vals2, color='#d62728', linewidth=2.5, label=player2)
    ax.fill(angles, vals2, color='#d62728', alpha=0.25)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # 3. Giới hạn thang đo
    ax.set_ylim(0, 115)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], color="gray", size=8)
    ax.set_thetagrids(np.degrees(angles[:-1]), display_labels, fontsize=10, weight='bold')
    ax.tick_params(pad=14)

    # 4. TIÊU ĐỀ: Dùng suptitle đặt ở vị trí y=0.96 (nằm hoàn toàn bên trong ảnh, không bị cắt)
    # 4. TIÊU ĐỀ: Đặt 1 dòng duy nhất ở trên đỉnh (y=0.96), không ngắt dòng
    fig.suptitle(
        f"So sánh chỉ số (Thang 100): {player1} vs {player2}",
        fontsize=13,
        fontweight='bold',
        y=0.96
    )

    # 5. Chú thích đặt góc dưới bên phải
    ax.legend(loc='lower left', bbox_to_anchor=(0.82, -0.05), fontsize=10, frameon=True)

    # 6. ĐẶC BIỆT: Đặt top=0.76 để đẩy toàn bộ vòng tròn lùi xuống dưới, chữ Gls không bao giờ chạm tiêu đề
    plt.subplots_adjust(top=0.76, bottom=0.1, left=0.1, right=0.9)

    out_file = f"radar_{player1.replace(' ', '_')}_vs_{player2.replace(' ', '_')}.png"
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"[+] Đã tạo biểu đồ radar và lưu vào '{out_file}' thành công!")

def main():
    parser = argparse.ArgumentParser(description="Vẽ biểu đồ Radar so sánh 2 cầu thủ.")
    parser.add_argument("--p1", type=str, required=True, help="Tên cầu thủ thứ nhất")
    parser.add_argument("--p2", type=str, required=True, help="Tên cầu thủ thứ hai")
    parser.add_argument("--Attribute", type=str, required=True, help="Danh sách thuộc tính")

    args = parser.parse_args()
    attrs = [a.strip() for a in args.Attribute.split(",") if a.strip()]

    df = pd.read_csv("results.csv")
    plot_radar(df, args.p1, args.p2, attrs)

if __name__ == "__main__":
    main()