import itertools
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.stats.api as sms
from scipy.stats import ttest_1samp, shapiro, levene, ttest_ind, \
    mannwhitneyu, pearsonr, spearmanr, kendalltau, f_oneway, kruskal
from statsmodels.stats.proportion import proportions_ztest

pd.set_option("display.expand_frame_repr",False)
pd.set_option("display.float_format",lambda x: "%.4f" % x)


df_control = df_control_.copy()
df_test = df_test_.copy()

df_control.head()
df_control.info()
df_control.describe().T
df_control.shape

df_test.head()
df_test.describe().T
df_test.info()
df_test.shape
#####################################
# grafikler
#####################################

#####################################
# IS PROBLEMI
"""
Facebook kisa sure once mevcut "maximumbidding"
adi verilen teklif verme turune alternatif olarak
yeni bir teklif turu olan "averagebidding"’i tanitti.
Musterilerimizden biri olanbombabomba.com, 
bu yeni ozelligi test etmeye karar verdi ve
averagebidding'in maximumbidding'den daha fazla donusum 
getirip getirmediginianlamak icin birA/B testiyapmak istiyor.
A/B testi 1 aydir devam ediyor ve bombabomba.com
simdi sizden bu A/B testinin sonuclarini analiz etmenizi bekliyor.
Bombabomba.com icin nihai basari olcutu Purchase'dir. 
Bu nedenle, istatistiksel testler icin Purchase metrigine odaklanilmalidir.
"""
#####################################

#####################################
# VERİ SETİ HİKAYESİ
"""
Bir firmanin web site bilgilerini iceren bu veri setinde kullanicilarin
gordukleri ve tikladiklari reklam sayilari gibi bilgilerin yani sira 
buradan gelen kazanc bilgileri yer almaktadir.Kontrol ve Test grubu olmak
uzere iki ayri veri seti vardir. Bu veri setleriab_testing.xlsx excel’inin
ayri sayfalarinda yer almaktadir. Kontrol grubuna Maximum Bidding, 
test grubuna AverageBidding uygulanmistir.
"""
# IMPRESSION : REKLAM GORUNTULEM SAYISI
# CLICK      : GORUNTULENEN REKLAMA TIKLAMA SAYISI
# PURCHASE   : TIKLANILAN REKLAMLAR SONRASI SATIN ALININ URUN SAYISI
# EARNING    : SATIN ALINAN URUNLER SONRASI ELDE EDİLEN KAZANC
#####################################

#####################################
# GOREV 1: VERIYI ANALIZ ETME
#####################################
# GOREV 1 ADIM 1:
# TODO: veri setini oku
# TODO: control ve test veri setini ayrı degiskenlere ata
#####################################
df_control_ = pd.read_excel("ab_testing.xlsx",sheet_name="Control Group")
df_test_    = pd.read_excel("ab_testing.xlsx",sheet_name="Test Group")
df_control = df_control_.copy()
df_test = df_test_.copy()

#####################################
# GOREV 1 ADIM 2:
# TODO: control ve test grubu verilerini analiz ediniz
#####################################
# ---- control set ----
df_control.head()
df_control.info()
df_control.describe().T
df_control.shape
# ---- test set ----
df_test.head()
df_test.describe().T
df_test.info()
df_test.shape
#####################################
# GOREV 1 ADIM 3:
# TODO: analizden sonra concat metodunu kullanarak ve control verilerini birlestiriniz
#####################################
# ---- pd.series'e cevirme islemi
df_concat = pd.concat([df_control,df_test],keys=["control","test"])
df_concat.reset_index(inplace=True)
df_concat.tail()
df_concat.drop("level_1",axis=1,inplace=True)
df_concat.columns = ["dtype","impression","click","purchase","earning"]
df_concat.sample(10)
df_test.head()
df_control.head()
#####################################
# GOREV 2: A/B TESTININ HIPOTEZLERININ TANIMLANMASI
#####################################
# GOREV 2 ADIM 1:
# TODO: hipotezleri tanımla
#####################################
"""
oran olusturulur: 
click/impression: reklama tiklayanlar / goruntuleyenler
"""
# H0: control ve test veri seti arasında click/impression oranlari bakimindan istatistiksel olrak anlamlı bir farklılık yoktur.
# H1: control ve test veri seti arasında click/impression oranlari bakimindan istatistiksel olrak anlamlı bir farklılık vardir.
# H0: p1 = p2
# H1: p1 != p2

#####################################
# GOREV 2 ADIM 2:
# TODO: kontrol ve test grubu icin purchase ortalamalarini analiz edin
#####################################
p = df_concat.groupby("dtype").agg({"click":"sum",
                                "impression":"sum",
                                "purchase":"mean"})
p1_control = 204026.2949/4068457.9627
p2_test    = 158701.9904/4820496.4703

reklama_tiklayan = p.values[:,0]
reklami_goruntuleyen = p.values[:,1]

df_concat["ci_ratio"] = df_concat["click"] / df_concat["impression"]

df_concat.groupby("dtype").agg({"ci_ratio":"mean",
                                "purchase":"mean"})

#####################################
# GOREV 3: HIPOTEZ TESTININ GERCEKLESTIRILMESI
#####################################
# GOREV 3 ADIM 1:
# TODO: test ve kontrol gruplari icin varsayim kontrolu yap
#####################################
# ---- normallik varsayimi ----
# H0: standart normal dagilim ile control/test veri setinin purchase degiskeninin dagilimi arasında istatistiksel olarak anlamli bir farklilik yoktur.
# H1: standart normal dagilim ile control/test veri setinin purchase degiskeninin dagilimi arasında istatistiksel olarak anlamli bir farklilik vardir.
# H0: dagilim normal dagilima uyar.
# H1: dagilim normal dagilima uymaz.
for type in list(df_concat["dtype"].unique()):
    test_stat, p_value = shapiro(df_concat.loc[df_concat["dtype"]==type,"purchase"])
    print(type,"veri seti :","test degeri : %.4f,  p value : %.4f" % (test_stat,p_value))
# ---- normallik varsayimi sonuc ----
""" p value > 0.05 H0 reddedilemez. (normallik varsayimi saglanmistir.) """

# ---- varyans homojenligi varsayimi ----
# H0: varyans homojenligi saglanmistir
# H1: varyans homojenligi saglanmamistir.
test_stat, p_value = levene(df_concat.loc[df_concat["dtype"]=="control","purchase"],
                            df_concat.loc[df_concat["dtype"]=="test","purchase"])
print("test degeri : %.4f,  p value : %.4f" % (test_stat,p_value))
# ---- varyans homojenligi varsayimi sonuc ----
""" p value > 0.05 H0 reddedilemez. (varyans homojenligi saglanmistir.) """

#####################################
# GOREV 3 ADIM 2:
# TODO: varsayim kontrolu sonrası uygun testi seciniz
#####################################
"""normallik ve varyans homojenligi varsayimlari saglandigi icin parametrik yöntem
tercih edilir (porportion_ztest uygulanacak) - varsayimlarin ikisi de saglandigi icin equal_var= True - """

test_stat, p_value = proportions_ztest(reklama_tiklayan, reklami_goruntuleyen)
print("test degeri : %.4f , p value : %.4f " % (test_stat,p_value))

#####################################
# GOREV 3 ADIM 3:
# TODO: sonuclari yorumla
#####################################
""" p value < 0.05 yani en basta kurdugumuz H0 hipotezi reddedilir. 
control ve test olarak olusturulmus iki farkli tasarıma ait veri setlerinin ortalama purchase degeri 
hesaplandiginda meydana gelen farklilik tesadufi degildir, istatistiksel olarak anlamli bir farklilikdir.
"""

#####################################
# GOREV 4: HIPOTEZ TESTININ GERCEKLESTIRILMESI
#####################################
# GOREV 4 ADIM 1:
# TODO: hangi test neden kullanildi, sebepler ?
#####################################
""" incelemelerimiz oran üzerinden oldugu için anahipotezimizi sorgulamak adına proprotion_ztest kullandık
normallik ve varyans homojenligi kısmında ise sirasiyla shapiro ve levene  testleri ile alt hipotezlerimizin 
dogrulugunu sinadik."""
#####################################
# GOREV 4 ADIM 2:
# TODO: sonuclara gore aksiyon fikirleriniz?
#####################################
""" ana hipotezimizin p value'su 0.05 den kücük oldugu icin iki tasarımın ortalama purchase uzerinde farklı geri dosnusum 
oranlarina sahip olmasının tamamen tesaduften ibaret oldugunu saavunan H0 hipotezimizi reddederiz.bu sayede uygulamamizin 
basinda olctugumuz geri donusum oranlarından daha yuksek olan control veri setine uygulanan tasarımın bariz bir sekilde 
daha iyi sonuclar aciga cikardigi gorulmektedir.uygulamanin bu andan itibaren control 
veri setindeki haliyle kalmasi mantikli karar olacaktir."""