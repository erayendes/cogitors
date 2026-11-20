# Değişiklikler

🇬🇧 [English](../CHANGELOG.md)

## Yayınlanmadı

### Değişenler
- `/voltron` ve `/lions`'ta ana model artık Elder değil Siyah Aslan (Elder `/cogitors`'ta kalır). `cogitor.py voltron --elder` artık `--black-lion`; sonuçtaki `elder` alanı `black_lion` oldu.
- Bir çalışmadaki her aslan Voltron'un renklerinden birini alır (kırmızı, sarı, yeşil, mavi); renkler plana göre karışır, `--check` ve sonuçlarda `color` olarak görünür; dağıtım satırları renkle başlar.
- Aynı anda en fazla dört aslan çalışır: Siyah Aslan'la birlikte Voltron'u oluşturan beş aslan olurlar.

## 0.3.1

### Eklenenler
- Antigravity kotası: `"usage": {"antigravity": "acp"}` ile `cogitors quota`, agy'nin 5 saatlik ve haftalık pencerelerini kısa bir yerel `agy acp` oturumundan okur (model çağrısı yok, token okunmaz, geride konuşma kalmaz); sonuç beş dakika önbellekte tutulur.
- Öneri kaydı: `cogitors proposal --kind voltron|lions --answer accepted|declined` her `/voltron` ya da `/lions` önerisini ve yanıtı kaydeder; `cogitors metrics` bunları `proposals` altında özetler.

### Değişenler
- `/voltron` ve `/lions` her işte tartılır ve gerekçe ile aslan planıyla önerilir (yine önce sorulur).
- Kesin bir kota hatasından sonra `/codex`, `/claude` ve `/antigravity`, sormadan bir kez kotası olan başka bir yetkin modele, hesaba ya da CLI'ya geçer ve bunu söyler; zaman aşımı ve diğer hatalar yine hiç yeniden denenmez. Aslanlar da aynı şekilde devredilir. `cogitors` katı kalır.
- Aslan seçimi: simülatör ya da arayüz gerektiren iş ona erişebilen aslana gider, inceleme başka model ailesini tercih eder, kotası azalan Elder işin daha çoğunu kotası olan aslanlara verir.
- Antigravity havuzları agy'nin kendi kota gruplarını izler: `gemini`, `argon` (ayrı) ve `claude` (Claude ve GPT-OSS); eski `other` havuzu kaldırıldı.
- Önce kotaya göre aslan seçimi: Elder kotası tükenen aslanları atlar, penceresi en erken yenilenen kotası müsait ajanı tercih eder (haftalık pencereler 5 saatliklerden önce, `unknown` en sonda gelir), yetkinliği yalnızca işi hiç yapamayan ajanları elemek için kullanır ve model ile effort'u işin boyutuna ve riskine göre canlı `cogitors models` listesinden seçer (`routing` yedek listeleri yine önceliklidir).
- Elder kota yedeği: Elder Voltron oluşturmadan ya da aslanları göndermeden önce iş için kendi yönetim payını tahmin eder, bunu kalan kotasıyla birlikte planda belirtir, kotası bu payın altındaysa ya da bilinmiyorsa birleştirme ve doğrulamayı da bir aslana devreder ve kısa yapılandırılmış raporlarla kendi kullanımını düşük tutar.
- `cogitors`, kullanıcıya model ve effort seçtirirken seçeneklerin yanında `cogitors quota` çıktısını gösterir; ancak katı kalır (kendiliğinden model değiştirmez).
- Antigravity model–kota grubu eşlemesi sabit model adları yerine doğrudan agy'nin kendi kota özetinden ve `agy models` görünen adlarından türetilir.

## 0.3.0

### Eklenenler
- `cogitors quota`, her aslanın kalan kotasını model çağırmadan, ağa çıkmadan ve token okumadan gösterir. Claude aslanları bir status-line anlık görüntüsünü (`~/.cogitors/config.json` içindeki `usage`), Codex aslanları en yeni oturum dosyalarındaki en son hesap geneli ölçümü okur; Antigravity için yalnızca cooldown vardır.
- Kota defteri `~/.cogitors/quota.json`, bir aslan kesin bir kota hatası aldığında cooldown kaydeder.
- Yönlendirme katmanları: plandaki bir aslan `tier` (`light`, `standard`, `deep`) taşıyabilir; plan belirtmedikçe modeli ve effort'u yapılandırmadaki `routing`'den gelir.
- Elder `/voltron` ve `/lions` önerisini kendiliğinden getirebilir, ama önce sorar.
- Bir yönlendirme katmanı sıralı bir aslan yedek listesi olabilir; `quota --json` her adımın durumunu `fallbacks` altında gösterir.
- Her `voltron` çalışması `~/.cogitors/runs.jsonl` dosyasına aslan başına bir satır ekler (istem, yanıt ya da hata metni yok); `cogitors metrics` aslan ve model başına süre, başarı ve kota oranını özetler.
- `/voltron` ve `/lions` brief'leri teslim sözleşmesi taşır ve neyin bitmiş sayılmadığını yazar; yalnızca kanıtlı bulgu engeller, aynı model ailesinin hemfikir olması doğrulama sayılmaz.

### Değişenler
- `cogitors voltron`, kotası tükenmiş bir aslanı, aslanı ve sıfırlanma zamanını belirterek, hiçbir model çalışmadan reddeder.
- Kesin kota hatası alan aslanın parçası artık yalnızca aynı CLI'nin başka bir modeline değil, kotası olan başka bir yetkin aslana (aynı CLI'nin başka bir hesabı dahil) veriliyor.
- Başarısız bir Codex çalışması artık stderr'deki kapanış satırı yerine Codex'in kendi hata mesajını bildiriyor.
- Eski biçimli yapılandırma (düz `{agent: options}`), yanına `usage` ya da `routing` eklenince kayıtlı modellerini kaybetmiyor.
- Antigravity'nin çevrimdışı yedek model listesi artık Argon'u varsayılan yapmıyor; varsayılan `gemini-4-neon-high`.
- `cogitors` kendisi katı kalır: otomatik yeniden deneme, model ya da hesap değişikliği yok.

## 0.2.2

### Değişenler
- Başarısız olan bir aslan artık yalnızca çıkış kodunu değil, CLI'sının son mesajını da (örneğin bir kota hatası) bildiriyor.
- `cogitors voltron`, en az bir aslan başarılı olduysa 0 ile çıkıyor; kısmi bir çalışma artık başarısız gibi görünmüyor.
- `/voltron` her zaman Voltron'u oluşturmaktan söz ediyor.
- Modelinin kotası dolan aslan `quota` olarak işaretleniyor; Elder onun parçasını aynı CLI'nin başka bir modeliyle bir kez yeniden çalıştırıyor ve bunu size söylüyor.

## 0.2.1

### Yeni
- **/lions:** Elder dışındaki her model ve hesap aynı görevi kendi bakış açısından yapar; Elder bulguları birleştirir. 0.2.0'daki `/voltron` böyle çalışıyordu.
- **Modelli plan:** `/voltron` ve `/lions` için Elder her aslanın modelini, effort'unu ve işini yazan bir plan hazırlar, gösterir ve hemen başlar. `cogitors voltron --plan` planı çalıştırır.
- **Güncel model listeleri:** `cogitors models`, Codex ve Antigravity modellerini kendi CLI'larından okur; Claude listesi güncel takma adları kullanır.

### Değişenler
- **/voltron** artık işi parçalara böler: her aslan kendi dosyaları içinde bir parçayı yapar, Elder parçaları birleştirip testleri çalıştırır. Bir aslanın kendi parçası dışında değiştirdiği dosyalar bildirilir.
- Dosya değiştiren aslanlar, çalışma klasörünün o anki hâlinden başlar; commit edilmemiş ve izlenmeyen dosyalar dahil. Böylece Elder ortak zemini commit etmeden hazırlayabilir.

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
