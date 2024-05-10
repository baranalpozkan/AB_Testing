########################################################################
# AB Testi ile Bidding Yöntemlerinin Dönüşümünün Karşılaştırılması
########################################################################

########################################################################
# İş Problemi
########################################################################

# Facebook kısa süre önce mevcut "maximum bidding" adı verilen teklif verme
# türüne alternatif olarak yeni bir teklif türü olan "average bidding"’i tanıttı.
# Müşterilerimizden biri olan bombabomba.com, bu yeni özelliği test etmeye karar verdi
# ve average bidding'in maximum bidding'den daha fazla dönüşüm getirip getirmediğini anlamak için bir A/B testi yapmak istiyor.
# A/B testi 1 aydır devam ediyor ve bombabomba.com şimdi sizden bu A/B testinin sonuçlarını analiz etmenizi bekliyor.
# Bombabomba.com için nihai başarı ölçütü Purchase'dır.
# Bu nedenle, istatistiksel testler için Purchase metriğine odaklanılmalıdır.

########################################################################
# Veri Seti Hikayesi
########################################################################

# Bir firmanın web site bilgilerini içeren bu veri setinde kullanıcıların gördükleri
# ve tıkladıkları reklam sayıları gibi bilgilerin yanı sıra buradan gelen kazanç bilgileri yer almaktadır.
# Kontrol ve Test grubu olmak üzere iki ayrı veri seti vardır.
# Bu veri setleri ab_testing.xlsx excel’inin ayrı sayfalarında yer almaktadır.
# Kontrol grubuna Maximum Bidding, test grubuna Average Bidding uygulanmıştır.

# Impression: Reklam görüntüleme sayısı
# Click: Görüntülenen reklama tıklama sayısı
# Purchase: Tıklanan reklamlar sonrası satın alınan ürün sayısı
# Earning: Satın alınan ürünler sonrası elde edilen kazanç

########################################################################
# Görev 1: Veriyi Hazırlama ve Analiz Etme
########################################################################

# Adım 1: ab_testing_data.xlsx adlı kontrol ve test grubu verilerinden oluşan veri setini okutunuz.
# Kontrol ve test grubu verilerini ayrı değişkenlere atayınız.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import shapiro, levene, ttest_ind

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 500)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

dataframe_control = pd.read_excel("cases/case1/ab_testing.xlsx", sheet_name="Control Group")
dataframe_test = pd.read_excel("cases/case1/ab_testing.xlsx", sheet_name="Test Group")

df_control = dataframe_control.copy()
df_test = dataframe_test.copy()

# Adım 2: Kontrol ve test grubu verilerini analiz ediniz.

def check_df(dataframe, head=5):
    print("#################### Shape ####################")
    print(dataframe.shape)
    print("#################### Info ####################")
    print(dataframe.info())
    print("#################### Types ####################")
    print(dataframe.dtypes)
    print("#################### Head ####################")
    print(dataframe.head(head))
    print("#################### Tail ####################")
    print(dataframe.tail(head))
    print("#################### Null ####################")
    print(dataframe.isnull().sum())
    print("#################### Describe ####################")
    print(dataframe.describe().T)
    print("#################### Quantiles ####################")
    print(dataframe.quantile([0, 0.05, 0.50, 0.95, 0.99, 1]).T)


check_df(df_control)
check_df(df_test)

# Adım 3: Analiz işleminden sonra concat metodunu kullanarak kontrol ve test grubu verilerini birleştiriniz.

df_control["group"] = "control"
df_test["group"] = "test"

df = pd.concat([df_control, df_test], axis=0, ignore_index=True)
df.head()
df.tail()

########################################################################
# Görev 2: A/B Testinin Hipotezinin Tanımlanması
########################################################################

# Adım 1: Hipotezi tanımlayınız.

# H0 : M1 = M2 (Kontrol grubu ve test grubu ortalamalarında istatistiksel olarak anlamlı bir fark yoktur.)
# H1 : M1!= M2 (Kontrol grubu ve test grubu ortalamalarında istatistiksel olarak anlamlı bir fark vardır.)

# Adım 2: Kontrol ve test grubu için purchase (kazanç) ortalamalarını analiz ediniz.

df.groupby("group").agg({"Purchase": "mean"})

########################################################################
# Görev 3: Hipotez Testinin Gerçekleştirilmesi
########################################################################

# Adım 1: Hipotez testi yapılmadan önce varsayım kontrollerini yapınız.
# Bunlar Normallik Varsayımı ve Varyans Homojenliğidir.
# Kontrol ve test grubunun normallik varsayımına uyup uymadığını Purchase değişkeni üzerinden ayrı ayrı test ediniz.

# Normallik Varsayımı :
# H0: Normal dağılım varsayımı sağlanmaktadır.
# H1: Normal dağılım varsayımı sağlanmamaktadır.
# p < 0.05 H0 RED , p > 0.05 H0 REDDEDİLEMEZ

# Test sonucuna göre normallik varsayımı kontrol ve test grupları için sağlanıyor mu ?
# Elde edilen p-value değerlerini yorumlayınız.

test_stat, pvalue = shapiro(df.loc[df["group"] == "control", "Purchase"])
print('Test Stat = %.5f, p-value = %.5f' % (test_stat, pvalue))

test_stat, pvalue = shapiro(df.loc[df["group"] == "test", "Purchase"])
print('Test Stat = %.5f, p-value = %.5f' % (test_stat, pvalue))

# p-value'lar hem test hem kontrol grupları için de 0.05'ten büyük olduğu için normallik H0 hipotezi reddedilemez.

# Varyans Homojenliği :
# H0: Varyanslar homojendir.
# H1: Varyanslar homojen Değildir.
# p < 0.05 H0 RED , p > 0.05 H0 REDDEDİLEMEZ

# Kontrol ve test grubu için varyans homojenliğinin sağlanıp sağlanmadığını Purchase değişkeni üzerinden test ediniz.
# Test sonucuna göre varyans homojenliği varsayımı sağlanıyor mu? Elde edilen p-value değerlerini yorumlayınız.

test_stat, pvalue = levene(df.loc[df["group"] == "control", "Purchase"],
                           df.loc[df["group"] == "test", "Purchase"])
print('Test Stat = %.5f, p-value = %.5f' % (test_stat, pvalue))

# p-value 0.05'ten büyük olduğu için varyans homojenliği H0 hipotezi reddedilemez.

# Adım 2: Normallik Varsayımı ve Varyans Homojenliği sonuçlarına göre uygun testi seçiniz.
# Varsayımlar sağlandığı için parametrik test olan bağımsız iki örneklem t testi yapılacaktır.

# H0: M1 = M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında ist. ol.anl.fark yoktur.)
# H1: M1 != M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında ist. ol.anl.fark vardır)
# p<0.05 HO RED , p>0.05 HO REDDEDİLEMEZ

test_stat, pvalue = ttest_ind(df.loc[df["group"] == "control", "Purchase"],
                              df.loc[df["group"] == "test", "Purchase"],
                              equal_var=True)
print('Test Stat = %.5f, p-value = %.5f' % (test_stat, pvalue))

# Adım 3: Test sonucunda elde edilen p_value değerini göz önünde bulundurarak kontrol ve
# test grubu satın alma ortalamaları arasında istatistiki olarak anlamlı bir fark olup olmadığını yorumlayınız.

# pvalue değeri 0.05'ten büyük olduğu için H0 hipotezi reddedilemez, dolayısyıla kontrol grubu ve test grubu satın alma ortalamaları
# arasında istatistiksel olarak anlamlı bir fark yoktur.


########################################################################
# Görev 4: Sonuçların Analizi
########################################################################

# Adım 1: Hangi testi kullandınız, sebeplerini belirtiniz.

# Normallik ve varyans homojenliği varsayımları sağlandığı için parametrik bir test olan bağımsız iki örneklem t testi kullanıldı.

# Adım 2: Elde ettiğiniz test sonuçlarına göre müşteriye tavsiyede bulununuz.

# Satın alma anlamında anlamlı bir fark olmadığından müşteri iki yöntemden herhangi birisini tercih edebilir.
# Fakat burada diğer istatistiklerdeki farklılıklar da önem arz etmektedir. Tıklanma, Etkileşim, Kazanç ve Dönüşüm Oranlarındaki farklılıklar
# değerlendirilip hangi yöntemin daha kazançlı olduğu tespit edilebilir. Özellikle Facebook'a tıklanma başına para ödendiği için
# hangi yöntemde tıklanma daha az olduğu tespit edilip ve CTR (Click Through Rate - Tıklama Oranı) oranına bakılabilir.
# İki grup gözlenmeye devam edilir.


























