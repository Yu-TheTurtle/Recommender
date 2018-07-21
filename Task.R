#preprocessing
per = perceptual_data_oct_2017_20180621[-1,]
per = per[-1,]

per = t(per)
View(per)

colnames(per) = per[1,]
per = per[-1,]


aperture = apply(vowels_features[-1,2:7],MARGIN = 2,as.integer)
aperture = factor((aperture %*% (1:ncol(aperture))) + 1, 
       labels = vowels_features[1,2:7])

tongue = apply(vowels_features[-1,8:11],MARGIN = 2,as.integer)
tongue = factor((tongue %*% (1:ncol(tongue))) + 1, 
       labels = vowels_features[1,8:11])

lip = apply(vowels_features[-1,12:13],MARGIN = 2,as.integer)
lip = factor((lip %*% (1:ncol(lip))) + 1, 
       labels = vowels_features[1,12:13])

oral = apply(vowels_features[-1,14:15],MARGIN = 2,as.integer)
oral = factor((oral %*% (1:ncol(oral))) + 1, 
       labels = vowels_features[1,14:15])

feature = data.frame(aperture, tongue, lip, oral)

#fill in the NA
per_original = per
per = data.frame(per)
is.na.data.frame(per)

for (i in 1:14){
  per[is.na(per[,i]),i] = names(which.max(table(per[,i])))
}

#read data
feature = read.csv('/Users/hsnu130427/Documents/??????/Python/Vowel/feature.csv')
per = read.csv('/Users/hsnu130427/Documents/??????/Python/Vowel/per.csv',
               header = TRUE)

View(feature)
View(per)
feature$ap_dis = substring(feature$aperture,first=9) %>% as.numeric()
feature$t_dis = substring(feature$tongue,first=7) %>% as.numeric()



#visualization
library(ggplo2)
qplot(data = feature, x=tongue,y=aperture,
      color=feature$nation,shape =lip,size=3,
      geom = 'jitter')

p = ggplot(data = feature, aes(x=tongue,y=aperture,shape=lip))

library(ggthemes)


p + geom_jitter(aes(colour = nation, size = 3)) + 
  theme_wsj() + scale_colour_wsj('colors6')# + ggtitle("Vowel")

p + geom_text(aes(colour = nation, size = 3,label = code)) + 
  theme_calc() + scale_colour_calc() #??????????????????

library(ggrepel)

p + geom_label_repel(aes(colour = nation, size = 3,label = code)) + 
  geom_jitter(aes(colour = oral)) + 
  theme_calc() + scale_colour_calc() +
  ggtitle('Feature Map for JP & FR vowels')


#per data 
library(dplyr)

per_table = apply(per, MARGIN = 2, FUN = table)

freq_table = rbind(fr1,fr2,fr3,fr4,fr5,fr6,fr7,fr8,fr9,fr10,fr11,fr12,fr13,fr14)

ggplot(data = freq_table, aes(x = code, y= Freq)) +
  geom_col(aes(fill=Var1),color ='black', width = 0.5) + 
  ggtitle('Vowel Data') + xlab('French Vowels') + ylab('Frequency')

ggplot(data = freq_table[freq_table$code %in% c('fr5','fr8','fr11'),], aes(x = code, y= Freq)) +
  geom_col(aes(fill=Var1),color ='black',width = 0.5) + 
  ggtitle('Three Abnormal Pattern') + xlab('French Vowels') + ylab('Frequency')
