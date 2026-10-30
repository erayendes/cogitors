# Değişiklikler

🇬🇧 [English](../CHANGELOG.md)

## 0.2.0

### Yeni
- **/voltron:** Aynı görevi Elder dışındaki tüm modellere ve hesaplara aynı anda verir; her biri bir aslan olarak çalışır. Elder raporları kontrol eder ve tek cevap verir. Dosya değiştiren görevlerde her aslan kendi git worktree'sinde çalışır. İkinci Claude ya da Codex girişleri `~/.cogitors/config.json` içinde `accounts` olarak tanımlanır.
- **Takip soruları:** HTML raporun her bölümünde bir **Sor** düğmesi var. Soruları tek tek ya da toplu kopyalayıp sohbete yapıştırırsınız. Elder model çağırmadan, oturum kaydından cevaplar; cevaplar sorulan bölümün altında görünür. Kararın metni değişmez.
- **Yeniden bakış:** Elder karara yeniden bakılacak bir tarih koyabilir. `cogitors revisit` tarihi gelen oturumları listeler. Her gerekçeli ayrışma, onu neyin netleştireceğini de yazabilir.
- **Oturum öncesi eleme:** Karar zaten verilmişse, yalnızca onay isteniyorsa ya da somut seçenek yoksa, model çağrısı yapılmadan önce bunu söyler.

### Değişenler
- Oturumlar artık `docs/cogitors/<tarih>-<konu>/` altında. Eski konum `docs/cogitors-decisions/` idi. Çalışma dosyaları git'in görmediği `temp/` klasöründe tutulur ve rapor bitince silinir.
- Ek hesaplar yalnızca genel config dosyasından okunur; klonlanan bir depo hesap klasörü seçemez.
- `configure -i` ve `init -i` terminal olmadan çalışmaz; eskisi gibi sessizce sabit modellere düşmez.

### Düzeltmeler
- `--git-diff HEAD` artık staged değişiklikleri de kapsıyor.
- Zaman aşımında yeniden deneme, oturum doğrulaması başarısız olduktan sonra da yeniden çalıştırılabiliyor.
- Değiştirilmiş ya da fazladan eklenmiş işler reddediliyor.
- `next_action`, dağıtım sürerken Elder'ın kendi görüşünü kaydetmesini öneriyor.
- Antigravity model adları (`gemini-3.1-pro-high`) artık yanlış bölünmüyor.
- Paketleme, üst klasörü olmayan bir hedefe de yazabiliyor.
