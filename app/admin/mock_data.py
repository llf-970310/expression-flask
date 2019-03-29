weight_data = {
    'keyWords': [['高铁', '高速铁路'], ['方式', '方法', '形式', '手段'], ['出行'], ['性价比', '受欢迎', '热门', '畅销', '出名'], ['速度', '速率'],
                 ['舒适', '不适感'], ['正点', '准点', '误点'], ['成本', '效率', '费用', '效益', '价格']],
    'keyWeight': [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125],
    'keyHitTimes': [10, 10, 10, 10, 10, 10, 10, 10],
    'detailWords': [['40', '四十', '6', '六', '贵阳', '昆明', '桂林', '成都', '柳州', '南宁', '贵州', '遵义', '蒙自'],
                    ['天气', '天候', '飞机', '直升机', '民航机', '起飞', '飞行中', '航空器'],
                    ['电源', '电池', '电路', '开关', '控制器', '元件', '设备', '餐车', '无线', 'wifi'], ['运营', '营运', '运行'], ['专业'],
                    ['管理', '监管', '行政']],
    'detailWeight': [0.167, 0.167, 0.167, 0.167, 0.167, 0.167],
    'detailHitTimes': [10, 10, 10, 10, 10, 10],
    'allHitTimes': 50,
}

score_data = {
    'key': [18.762, 24.803, 28.705, 31.686, 34.144, 36.263, 38.145, 39.851, 41.422, 42.886, 44.263, 45.570, 46.817,
            48.015, 49.172, 50.294, 51.385, 52.452, 53.498, 54.526, 55.540, 56.542, 57.536, 58.524, 59.508, 60.492,
            61.476, 62.464, 63.458, 64.460, 65.474, 66.502, 67.548, 68.615, 69.706, 70.828, 71.985, 73.183, 74.430,
            75.737, 77.114, 78.578, 80.149, 81.855, 83.737, 85.856, 88.314, 91.295, 95.197, 100],
    'detail': [21.009, 25.842, 28.964, 31.349, 33.315, 35.011, 36.516, 37.881, 39.138, 40.309, 41.410, 42.456,
               43.454, 44.412, 45.338, 46.235, 47.108, 47.962, 48.798, 49.621, 50.432, 51.234, 52.029, 52.819,
               53.607, 54.393, 55.181, 55.971, 56.766, 57.568, 58.379, 59.202, 60.038, 60.892, 61.765, 62.662,
               63.588, 64.546, 65.544, 66.590, 67.691, 68.862, 70.119, 71.484, 72.989, 74.685, 76.651, 79.036,
               82.158, 86.991],
    'total': [19.436, 25.115, 28.783, 31.585, 33.895, 35.888, 37.657, 39.260, 40.737, 42.113, 43.407, 44.635,
              45.808, 46.934, 48.022, 49.076, 50.102, 51.105, 52.088, 53.054, 54.007, 54.950, 55.884, 56.813,
              57.738, 58.662, 59.587, 60.516, 61.450, 62.393, 63.346, 64.312, 65.295, 66.298, 67.324, 68.378,
              69.466, 70.592, 71.765, 72.993, 74.287, 75.663, 77.140, 78.743, 80.512, 82.505, 84.815, 87.617,
              91.285, 96.964],
    'keyStatistic': {"mean": 59.97524000000001, "sigma": 18.79245, "difficulty": 0.5997524000000001,
                     "discrimination": 0.22717785714285707},
    'detailStatistic': {"mean": 54, "sigma": 15.07761, "difficulty": 0.54, "discrimination": 0.18209571428571436},
    'totalStatistic': {"mean": 58.2, "sigma": 17.71612, "difficulty": 0.582, "discrimination": 0.21396214285714282},

}

cost_data = {
    "date": "2019-03-09", "finish": True,
    "costData": [{"itrTimes": 200, "cost": 13.6349}, {"itrTimes": 400, "cost": 12.9269},
                 {"itrTimes": 600, "cost": 12.2557}, {"itrTimes": 800, "cost": 11.6194},
                 {"itrTimes": 1000, "cost": 11.0161}, {"itrTimes": 1200, "cost": 10.4441},
                 {"itrTimes": 1400, "cost": 9.9018}, {"itrTimes": 1600, "cost": 9.3877},
                 {"itrTimes": 1800, "cost": 8.9003}, {"itrTimes": 2000, "cost": 8.4381},
                 {"itrTimes": 2200, "cost": 8}, {"itrTimes": 2400, "cost": 7.5846},
                 {"itrTimes": 2600, "cost": 7.1908}, {"itrTimes": 2800, "cost": 6.8174},
                 {"itrTimes": 3000, "cost": 6.4635}, {"itrTimes": 3200, "cost": 6.1279},
                 {"itrTimes": 3400, "cost": 5.8097}, {"itrTimes": 3600, "cost": 5.508},
                 {"itrTimes": 3800, "cost": 5.222}, {"itrTimes": 4000, "cost": 4.9509},
                 {"itrTimes": 4200, "cost": 4.6938}, {"itrTimes": 4400, "cost": 4.4501},
                 {"itrTimes": 4600, "cost": 4.2191}, {"itrTimes": 4800, "cost": 4},
                 {"itrTimes": 5000, "cost": 3.7923}, {"itrTimes": 5200, "cost": 3.5954},
                 {"itrTimes": 5400, "cost": 3.4087}, {"itrTimes": 5600, "cost": 3.2317},
                 {"itrTimes": 5800, "cost": 3.0639}, {"itrTimes": 6000, "cost": 2.9048},
                 {"itrTimes": 6200, "cost": 2.754}, {"itrTimes": 6400, "cost": 2.611},
                 {"itrTimes": 6600, "cost": 2.4755}, {"itrTimes": 6800, "cost": 2.3469},
                 {"itrTimes": 7000, "cost": 2.2251}, {"itrTimes": 7200, "cost": 2.1095},
                 {"itrTimes": 7400, "cost": 2}, {"itrTimes": 7600, "cost": 1.8962},
                 {"itrTimes": 7800, "cost": 1.7977}, {"itrTimes": 8000, "cost": 1.7044},
                 {"itrTimes": 8200, "cost": 1.6159}, {"itrTimes": 8400, "cost": 1.532},
                 {"itrTimes": 8600, "cost": 1.4524}, {"itrTimes": 8800, "cost": 1.377},
                 {"itrTimes": 9000, "cost": 1.3055}, {"itrTimes": 9200, "cost": 1.2377},
                 {"itrTimes": 9400, "cost": 1.1735}, {"itrTimes": 9600, "cost": 1.1125},
                 {"itrTimes": 9800, "cost": 1.0548}, {"itrTimes": 10000, "cost": 1}],
}

questions = {
    "count": 5,
    'questions': [
        {
            "questionId": 2,
            "rawText": "高铁是现在是最受欢迎的出行方式。首先，高铁速度快，比如说，以前从贵阳到北京，要用40个小时左右，但现在高铁只需要6个小时，大大减少了路途时间。其次，高铁正点率高，因为高铁受天气条件影响较小，通常都可以准时发车，按时到达。最后，高铁环境舒适，高铁坐席宽敞，运行时速度平稳，没有噪音，餐车环境整洁，配有电源插座和无线网络，乘坐高铁很少会造成不适感，对于不习惯坐飞机出行的人士，高铁是更理想的选择。但高铁的建设，前期投资非常巨大，对设备技术、制作工艺要求都很高，后期的管理运营也需要更专业的人员来完成。",
            "keywords": "「「高铁，高速铁路」，「方式，方法，形式，手段」，「出行」，「性价比，受欢迎，热门，畅销，出名」」",
            "mainwords": "「「速度，速率」，「舒适，不适感」，「正点，准点，误点」，「成本，效率，费用，效益，价格」」",
            "detailwords": "「「「40，四十，6，六，贵阳，昆明，桂林，成都，柳州，南宁，贵州，遵义，蒙自」，「天气，天候，飞机，直升机，民航机，起飞，飞行中，航空器」，「电源，电池，电路，开关，控制器，元件，设备，餐车，无线，wifi」」，「「运营，营运，运行」，「专业」，「管理，监管，行政」」」",
            "inOptimize": False,
            "lastOpDate": '2019-03-09',
        },
        {
            "questionId":
                3,
            "rawText":
                "城市会让生活更美好。在城市里居住，可以享受更多、更高质量的医疗和教育资源，生活的便利程度也更高。城市也是集聚人才，激发创意的地方，文艺复兴时候的佛罗伦萨，硅谷所在的旧金山都是典型的例子。另外，城市化也有利于国家经济模式的转型，从农业为主，往工业和第三产业的转型，2011年，中国的城市化率已经超过了50%。但城市也会带来拥挤、污染以及生育率下降等负面问题，需要更好的规划发展来解决。",
            "keywords":
                "「「美好，幸福，快乐」，「城市，郊区，大都市」，「生活」」",
            "mainwords":
                "「「资源」，「人才，人材」，「经济模式，市场经济」，「问题，难题」」",
            "detailwords":
                "「「「教育，教学」，「医疗，照护，卫生保健，诊疗，医护，公共卫生」，「质量」，「生活便利」」，「「硅谷，矽谷，佛罗伦萨，佛罗伦斯，旧金山，三藩市」，「创意，创新，创造力」」，「「转型」，「2011，一一，逐一，百分之五十，50」，「第三产业，服务业，第一产业，第二产业」，「工业，制造业，产业」，「城市化率」」，「「生育率，出生率」，「负面」，「污染，废水」，「规划，规画，建设」，「拥挤，挤迫，拥堵，交通堵塞」」」",
            "inOptimize": False,
            "lastOpDate": '2019-03-09',
        }
        ,
        {
            "questionId":
                4,
            "rawText":
                "玻璃，也就是二氧化硅，是一种非常重要的元素。硅元素在地球上的含量极其丰富，地壳里90%都是由硅元素组成的，因此玻璃的价格很便宜。玻璃的透光性很高，小到显微镜、电脑芯片，大到天文望远镜和连接全球的光纤，都离不开它。玻璃纤维的强度非常大，从制作防弹衣，到组成空客A380飞机的机身，玻璃纤维都是重要的材料。但玻璃也有弹性差、易碎的特点，破碎后容易伤人。",
            "keywords":
                "「「二氧化硅」，「玻璃」，「元素」，「重要，最主要，举足轻重，关键，不可或缺，不可忽视」」",
            "mainwords":
                "「「丰富，多样，大，多」，「透光性」，「用途，用作，用处」，「强度，硬度，坚硬」，「伤人，伤害」」",
            "detailwords":
                "「「「90，九十」，「地壳」，「含量，浓度，所含」，「便宜，低廉，廉价，廉宜」」，「「电脑芯片」，「光纤」，「显微镜，光学，透镜」，「望远镜」」，「「防弹衣，防弹背心」，「空客，空中客车，空中巴士，客机，飞机，民航机，航空器，A380」，「纤维」」，「「弹性，刚性」，「易碎，脆弱」」」",
            "inOptimize": True,
            "lastOpDate": '2019-03-09',
        }
        ,
        {
            "questionId":
                5,
            "rawText":
                "咖啡是现代生活中非常重要的饮品。喝咖啡有许多好处，首先它可以提神醒脑，是很多上班族的必备。其次，喝咖啡对身体健康有好处，比如：咖啡利尿，可以帮助排出身体毒素；咖啡对降低癌症风险、过劳死风险都有一定作用。第三，咖啡有利于情绪培养。实验表明，人一天吸收300毫克的咖啡因，约3杯现煮咖啡，对一个人的机警程度和情绪都会带来良好的影响。但需要注意的是，喝咖啡的时间应该在早晨或餐后，而不能在随餐伴饮，而很多速溶咖啡为了口味，加入了大量脂肪和糖，不能多喝。",
            "keywords":
                "「「饮品，饮料」，「咖啡」，「现代，当代」，「生活」，「重要，最主要，举足轻重，关键，不可或缺，不可忽视，不可缺少」」",
            "mainwords":
                "「「提神」，「健康」，「情绪，焦虑，情感」，「注意，留意，缺点，负面」」",
            "detailwords":
                "「「「上班，办公室，白领，公司」，「好处，益处，优点」」，「「利尿，排水」，「毒素，有毒」，「过劳死」，「癌」」，「「情绪，焦虑，情感」，「300，三，3」，「机警，机灵」，「咖啡因」」，「「早晨，早上，清晨，餐后，随餐」，「速溶」，「糖」，「脂肪，油脂」」」",
            "inOptimize": False,
            "lastOpDate": '2019-03-09',
        }
        ,
        {
            "questionId":
                6,
            "rawText":
                "旅游是很好的休闲方式，比起跟团游，现在更多人选择自由行，2016年，有57%的人选择了自由行。自由行的好处很多，首先，它可以按照个人喜好制定行程和游玩地点，不用千篇一律。其次，自由行的质量也更高，比起跟团游上车睡觉，下车拍照的方式，自由行可以深入游览，体验风土人情。自由行也更符合每个人的生活习惯，习惯晚起的人不用一大早就去赶团队行程，饮食选择、住宿选择也更多样化。但自由行对出行者的经验要求较高，要提前做功课，了解游玩地点；遇到突发状况也都要自己处理，需要很强的风险防范意识和应对能力。",
            "keywords":
                "「「自由行」，「跟团游，旅游，观光」，「方式，方法，形式，手段」，「好处，优点，益处，优势」」",
            "mainwords":
                "「「喜好，爱好，嗜好，喜欢，口味」，「质量」，「习惯，个性化，定制」，「经验，专业知识，经历」」",
            "detailwords":
                "「「「57，五十七，60，六十」，「2016，一六」，「千篇一律，类似，一样」，「行程，路线，攻略」，「地点，景点」」，「「深入，当地」，「风土人情，见闻，体验，体会」」，「「住宿，住」，「饮食，吃」，「多样化，多元化」，「时间」」，「「突发状况，突发，应对」，「风险，可能性，防范」，「提前，准备，功课，了解」」」",
            "inOptimize": False,
            "lastOpDate": '2019-03-09',
        }
    ]
}
