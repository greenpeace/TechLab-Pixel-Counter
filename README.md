# TechLab Tracking Pixel

<a href="https://github.com/greenpeace/gpes-multi-organizations-counter-api">Php version created by GPES</a> - 1. Osvalo's pixel code. It basically counts a pixel on the thank you page. 

Pros: Easy to implement across different digital marketing platforms.

Cons: Not too accurate. If somebody signs the petition twice, the email will be counted twice. 


GPUK Code. This is the <a href="https://act.greenpeace.org/page/49013/petition/1">counter</a> <a href="https://docs.google.com/document/d/1mXOSE4hpCNAhtNEJtkKpgsJ5lbFNVgU6sQnstAVemkk/edit#heading=h.1sym80nhaqvs">(see instructions)</a> that we are currently using to collate all unique signatures across different NROs working on plastics. This includes every single petition that NROs have launched  since the organisation started to campaign on plastics 5 years ago. As you can see some digital marketing platforms are not included in Jack's code so NROs that are on these platforms need to report their signatures every two months or so and we add them manually. The other NROs had to create dynamic lists/ IDs and include all of their plastics petitions. Their numbers get added to the counter automatically. You can see who is reporting manually and who has generated a list/ ID <a href="https://docs.google.com/spreadsheets/d/1jFyzV4Q34GLYZAu121uj1FZ4MoU6IP8XXkaKA9YTKQw/edit#gid=0">here</a> (look at the different tabs). 
Pros: More accurate
Cons: Not all digital platforms are supported, including our new global platform Hubspot so I need to do a lot of manual work. 

And a new vrsion create as a microservice using the Python Flask model