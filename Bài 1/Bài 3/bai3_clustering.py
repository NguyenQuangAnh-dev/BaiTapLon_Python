import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

def main():
    csv_file = "results.csv"
    print("[*] Đang nạp dữ liệu từ results.csv...")
    df = pd.read_csv(csv_file)

    # 1. Tiền xử lý dữ liệu: Tách các cột định danh và cột chỉ số định lượng
    id_cols = ["Player", "Nation", "Pos", "Squad", "Matches"]
    feature_cols = [c for c in df.columns if c not in id_cols]

    # Ép kiểu dữ liệu về dạng số thực (chuyển "N/a" thành NaN)
    for col in feature_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

    # Loại bỏ các cột có tỷ lệ thiếu dữ liệu quá cao (> 70%)
    valid_cols = [c for c in feature_cols if df[c].isna().mean() < 0.70]
    
    # Điền giá trị còn thiếu bằng 0 (vì thiếu dữ liệu chỉ số thường tương ứng với việc cầu thủ không thực hiện hành động đó)
    X = df[valid_cols].fillna(0)

    # Chuẩn hóa dữ liệu về cùng thang đo (Z-score scaling)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 2. Tìm số cụm K tối ưu bằng Elbow Method và Silhouette Score
    print("[*] Đang đánh giá số lượng cụm K tối ưu từ 2 đến 8...")
    inertias = []
    silhouette_scores = []
    k_range = range(2, 9)

    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        inertias.append(km.inertia_)
        silhouette_scores.append(silhouette_score(X_scaled, km.labels_))

    # Vẽ biểu đồ Elbow
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(k_range, inertias, marker='o', color='b')
    plt.title("Phương pháp Elbow (Inertia)")
    plt.xlabel("Số cụm (k)")
    plt.ylabel("Inertia")
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(k_range, silhouette_scores, marker='s', color='r')
    plt.title("Hệ số Silhouette")
    plt.xlabel("Số cụm (k)")
    plt.ylabel("Silhouette Score")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("kmeans_elbow_silhouette.png", dpi=300)
    plt.close()
    print("[+] Đã lưu biểu đồ đánh giá số cụm vào 'kmeans_elbow_silhouette.png'.")

    # 3. Phân cụm với K = 4 (tương ứng với 4 vai trò chính: GK, Hậu vệ, Tiền vệ, Tiền đạo)
    optimal_k = 4
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    df["Cluster"] = clusters

    print("\n" + "="*50)
    print(f"KẾT QUẢ PHÂN BỐ CẦU THỦ VÀO {optimal_k} CỤM:")
    print("="*50)
    for c in range(optimal_k):
        count = (clusters == c).sum()
        sample_players = df[df["Cluster"] == c]["Player"].head(5).tolist()
        print(f"Cụm {c} ({count} cầu thủ): Đại diện gồm {', '.join(sample_players)}")

    # 4. Giảm chiều dữ liệu xuống 2D bằng PCA và vẽ đồ thị
    print("\n[*] Đang áp dụng PCA giảm xuống 2 chiều...")
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)

    df["PCA1"] = X_pca[:, 0]
    df["PCA2"] = X_pca[:, 1]

    plt.figure(figsize=(10, 7))
    palette = sns.color_palette("tab10", optimal_k)
    sns.scatterplot(
        x="PCA1", y="PCA2", hue="Cluster", data=df,
        palette=palette, alpha=0.8, s=60, edgecolor="k"
    )

    # Gắn nhãn một vài cầu thủ tiêu biểu lên đồ thị để minh họa trực quan
    notable_players = ["Erling Haaland", "Mohamed Salah", "Virgil van Dijk", "Declan Rice", "Alisson"]
    for p in notable_players:
        p_row = df[df["Player"].str.contains(p, case=False, na=False)]
        if not p_row.empty:
            plt.text(p_row.iloc[0]["PCA1"] + 0.3, p_row.iloc[0]["PCA2"] + 0.3, p, fontsize=9, weight="bold")

    plt.title(f"Biểu đồ phân cụm cầu thủ (PCA 2D, K={optimal_k})")
    plt.xlabel(f"PCA 1 ({pca.explained_variance_ratio_[0]*100:.1f}% phương sai)")
    plt.ylabel(f"PCA 2 ({pca.explained_variance_ratio_[1]*100:.1f}% phương sai)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("pca_clusters_2d.png", dpi=300)
    plt.close()
    print("[+] Đã lưu biểu đồ PCA 2D vào file 'pca_clusters_2d.png'.")

    # Lưu lại file kết quả có cột Cluster phục vụ tra cứu
    df.to_csv("results_with_clusters.csv", index=False, encoding="utf-8-sig")
    print("[+] Đã lưu kết quả phân cụm chi tiết vào 'results_with_clusters.csv'.")

if __name__ == "__main__":
    main()