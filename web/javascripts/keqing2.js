$(function () {

    var imgpre = $('#IMGPRE').val()
    var lazy = $('#NOLAZY').val() ? '' : 'lazy'
    init_title('妮可少女的刻晴足迹 ' + computer_.MiscText.PAGE_TITLE[lang])

    var cur_time = Date.now()
    var days = Math.round((cur_time - 1619940323000) / 86400000).toString()

    $('.tls' + lang).css("color", "#df903b");
    $('h3 .title').html(computer_.MiscText.Title[lang] + "<color style='font-size: 26px;'><br>" + computer_.MiscText.game_img[lang] + VER_GI + "</b></color>");
    $('h3 .subtitle').html(computer_.MiscText.Subtitle[lang]);
    $('h3 .tlsub').html(computer_.MiscText.Translate_);
    $('h3 .tlsub').hide()
    $('h3 .links').render([
        {
            img: imgpre + 'images/menu.png',
            class: '_menu_'
        },
        {
            img: imgpre + 'images/translate.png',
            class: '_translate_'
        }
    ]);

    var Keqing_Data_Temp = [
    ]

    var Keqing_Data = [
        {
            title: '只有521万血还是别逗你刻晴姐笑了',
            bv: 'BV1Xq22BiEG9',
            date: '2025-12-09',
            cover: '760bd78472cd2c3b1fff582fac595974f3a912e2.jpg'
        },
        {
            title: '玉衡杯陨落后，我于刻晴诞生之日以「记忆」将其重塑',
            bv: 'BV19hCZBbE7Y',
            date: '2025-11-20',
            cover: '00000.png'
        },
        {
            title: '六年陪伴，携手向前！刻晴生贺：6.1幽境0+1+0金通解N5三间',
            bv: 'BV13YyEBUE5R',
            date: '2025-11-20',
            cover: 'Screenshot 2025-11-19 011321.png'
        },
        {
            title: '「6.1幽境」厨力爆炸！用刻晴拿金幻化#2：75秒N6天马',
            bv: 'BV1xXCNBeEAe',
            date: '2025-11-19',
            cover: 'Screenshot 2025-11-14 003042.png'
        },
        {
            title: '「6.1深渊」0金间均86s！膨胀下的最后一舞？0金刻皇极限满星上半！',
            bv: 'BV18VCeB9EvB',
            date: '2025-11-17',
            cover: 'Screenshot 2025-11-16 214551 (1).png'
        },
        {
            title: '「6.1深渊」震撼首发！1限定金刻皇0金队友满星全间！',
            bv: 'BV1i2CmBBECG',
            date: '2025-11-16',
            cover: 'Screenshot 2025-11-15 173607.png'
        },
        {
            title: '「6.0B深渊」献给你的生日礼物：0金刻皇满星深渊全间！',
            bv: 'BV1KCCGB9EqF',
            date: '2025-11-15',
            cover: '20251115.png'
        },
        {
            title: '「6.0B深渊」单推人陪伴刻晴的第六次生日！刻晴间均25s深渊下半三间',
            bv: 'BV1RoCKBSEMP',
            date: '2025-11-13',
            cover: 'Screenshot 2025-11-13 200515.png'
        },
        {
            title: '「6.1幽境」传统刻皇激化6.1还在蒸！豹草刻皇85秒通关N6霜役人',
            bv: 'BV1kmkfBCEFn',
            date: '2025-11-11',
            cover: 'Screenshot 2025-11-10 040047.png'
        },
        {
            title: '「6.1幽境」厨力爆炸！用刻晴拿金幻化#1：80秒N6天马',
            bv: 'BV1rD1VBREX5',
            date: '2025-10-31',
            cover: 'Screenshot 2025-10-31 193655 (2).png'
        },
        {
            title: '「砺行修远」一位晴宝厨终于等到了第15只晴宝😋',
            bv: 'BV1st1NBBE2P',
            date: '2025-10-30',
            cover: 'Screenshot 2025-10-30 202237.png'
        },
        {
            title: '跨越5年的主C「1」刻晴x奈芙尔深渊上下',
            bv: 'BV1mYyqBhEkf',
            date: '2025-10-27',
            cover: 'Screenshot 2025-10-27 215138 (1).png'
        },
        {
            title: '「6.0B深渊」展示厨力！刻晴耗时8:30单通1200万血狂猎！猜猜狂猎复活了多少次',
            bv: 'BV1SHsrz1EA3',
            date: '2025-10-26',
            cover: 'Screenshot 2025-10-26 145757.png'
        },
        {
            title: '「6.0B深渊」0金刻皇还在发力！间均81s肘击12层下半3间',
            bv: 'BV1Tys7zCE2t',
            date: '2025-10-23',
            cover: 'Screenshot 2025-10-23 210752.png'
        },
        {
            title: '「6.0B深渊」刻晴无敌了！3年前的0限定金队不走机制满星1400万12-2龙蜥+狂猎',
            bv: 'BV1RusTzdEX4',
            date: '2025-10-19',
            cover: 'Screenshot 2025-10-19 191447.png'
        },
        {
            title: '「6.0B深渊」感觉你是那种用3年前的刻皇激化肘击1000万狂猎的人',
            bv: 'BV1gNWfztEPU',
            date: '2025-10-18',
            cover: '5872eac28bdea2147c24b2c4a8198705b64f9a04.jpg'
        },
        {
            title: '「6.0B深渊」这是5年前的角色？刻晴间均22s上半，还不是满配！可以更快！',
            bv: 'BV1Y3WHzZEqh',
            date: '2025-10-17',
            cover: '6774c3cc6a3fe1ba1f080cdb141c27f54f921332.jpg'
        },
        {
            title: '「6.0B深渊」刻皇希妲60s千万血狂猎！',
            bv: 'BV1YiWezFE7k',
            date: '2025-10-15',
            cover: 'ff9f80c64fc4a3a44524c6bbddf83fa55f80eed1.jpg'
        },
        {
            title: '「6.0B深渊」盗水贤者万叶助刻晴暴斩12-3螃蟹！',
            bv: 'BV1GqWezbE5A',
            date: '2025-10-15',
            cover: 'c1a888998b73c244225fe9a6ab639bae4d4393e6.jpg'
        },
        {
            title: '「6.0幽境」真能玩到关服！五年老将还在发力！刻晴单推人的坚持，1限定金通关N5龙兽！',
            bv: 'BV1cU45zcEwe',
            date: '2025-10-09',
            cover: '41fa02ef04f70602db7a33cd9681f153043456ba.jpg'
        },
        {
            title: '「6.0幽境」玉衡不灭！刻+芙+妲 三C阵容93/88秒N6龙兽',
            bv: 'BV1nnxUzWEs9',
            date: '2025-10-06',
            cover: 'ae25d64a930280c9b6345d63b32a6209e968e2ea.jpg'
        },
        {
            title: '「6.0A深渊」都4年了刻皇还在蒸！低金上古刻皇满星12层，队里最新的五星是2.0的',
            bv: 'BV1gBxGzKENJ',
            date: '2025-10-05',
            cover: 'e163c9bf8a2cc7c2546605cff814a0b8c1a83c51.jpg'
        },
        {
            title: '「刻晴和冰刻晴」两个100级刻晴携手击破6.0A深渊',
            bv: 'BV1onJDzzEQN',
            date: '2025-09-23',
            cover: 'e2cb3b7e8043bc159287fcc66584bfe54ae1022d.jpg'
        },
        {
            title: '「6.0幽境」获得挪德卡莱新形态的刻晴！月激绽刻晴斩杀N6螃蟹！',
            bv: 'BV14EWMz1EiU',
            date: '2025-09-18',
            cover: 'db96d63b7a75445d4820f70467acbd117a668f10.jpg'
        },
        {
            title: '「6.0幽境」都6.0了，刻晴怎么还在通杀N6三路！月感电刻晴84s火刃突击队！',
            bv: 'BV1HQpWzLEFM',
            date: '2025-09-16',
            cover: '10e11adb23ae4f324ee0174a3734f37d072589b9.jpg'
        },
        {
            title: '「5.8幽境」刻晴又来暴打幽境了！82s拿下N6次数盾！',
            bv: 'BV1CJhSzrEgQ',
            date: '2025-08-28',
            cover: 'a8f516634933788fb7bd5841f44b7a3ef8531549.jpg'
        },
        {
            title: '「5.8幽境N6」都快挪德卡莱了，刻晴怎么还在发力？刻晴无伊涅芙74s难度6仙人掌！',
            bv: 'BV1J4bAzYEs6',
            date: '2025-08-10',
            cover: '486d9c6ccb10f1fa7565522cd2a03f64377b930a.jpg'
        },
        {
            title: '【5.7深渊】当我用两个刻晴分别打深渊上下半...',
            bv: 'BV1ijg3zqEda',
            date: '2025-07-19',
            cover: '9e1252d7690d8a9ae87912ccff30039a286e8585.jpg'
        },
        {
            title: '【5.7幽境】把不可能变为可能！刻晴主C通关幽境危战难度6！',
            bv: 'BV1ipKRzmEWj',
            date: '2025-06-26',
            cover: '14b1cb6ab83b5af118511e341caebf3c45a23818.jpg'
        },
        {
            title: '【5.6B深渊】刻晴你怎么这么坏😡你要毁掉丝玛深渊的付款码吗！',
            bv: 'BV1dANmzWEc8',
            date: '2025-06-21',
            cover: '9e406d59d3ddc2a3845e61c5d1c43bb369cd59ec.jpg'
        },
        {
            title: '【5.6B深渊】来点不一样的，上半全没犯错误，下半全犯过错误',
            bv: 'BV1GMNizHEdq',
            date: '2025-06-17',
            cover: '8f52d57884f92de32fcbc00b8ff9fde5395b2237.jpg'
        },
        {
            title: '【征战勇者淬炼之界】孩子们，我还能打！爬塔第1关刻晴23层',
            bv: 'BV1LJAdeEEUS',
            date: '2025-02-24',
            cover: '2bd5b714cead4b2886583ebc2e66c81652cb219a.jpg'
        },
        {
            title: '【5.4A深渊】用须弥的剑斩纳塔的官！刻晴纳西妲无伤双通 间均49s',
            bv: 'BV1LqPKe2EeN',
            date: '2025-02-21',
            cover: 'd7d1877fd5f65985a691a3e47d6e538363aa9f07.jpg'
        },
        {
            title: '【5.3风来人DAY1】刻晴5.3版本还能打？第一天60s拿下棱彩！',
            bv: 'BV1iocXeBE9c',
            date: '2025-01-13',
            cover: 'ac824ddb989cfb11c7954a5bb4e3d5df311fb7ce.jpg'
        },
        {
            title: '【殊形之龙】刻晴玩到关服！雷盾雷抗最高难度依旧拿下！',
            bv: 'BV17D42137Fx',
            date: '2024-05-27',
            cover: '96a6734fd7e6c8789ac4b9001b25886e2457151f.jpg'
        },
        {
            title: '600万鸡哥！玉皇妲帝全3星武器+绝弦68s无畏',
            bv: 'BV1uD42137Wi',
            date: '2024-05-25',
            cover: '15cc4d6f18be9e94e3d29657190adf7c225bf7a4.jpg'
        },
        {
            title: '不是哥们？刻晴三星武器都能74秒920万古岩龙蜥！',
            bv: 'BV1v1421i7tg',
            date: '2024-05-24',
            cover: '6a9b2bcd88b8488bcc9a77c7f441009b8130ecd0.jpg'
        },
        {
            title: '【殊形之龙】刻晴队46s无畏爆炎树！三年前的你，是否梦见过这一幕呢？',
            bv: 'BV1gb421z76h',
            date: '2024-05-22',
            cover: 'dc57c312b41084bf99f6cbd0a3727d010d4c9009.jpg'
        },
        {
            title: '【玉衡杯】刻晴单通80s水形幻人「比力量来源更重要的，是力量的驱使者」',
            bv: 'BV1KV411R7pi',
            date: '2024-01-12',
            cover: 'dd16f1d5db693c7dc690db955ad7f04f6aed468e.jpg'
        },
        {
            title: '【4.0深渊】守塔难？玉衡星孤军奋战100%守护上半',
            bv: 'BV1hH4y1Q7k7',
            date: '2023-09-01',
            cover: '5cd0c64ae0a70a521e71f07667b0563221df3019.jpg'
        },
        {
            title: '【离垢者肃心旅宴】刻晴 23s 8050 双子龙蜥（纪念）',
            bv: 'BV14F411d7Vy',
            date: '2023-06-26',
            cover: '4ac9f64efb55fe633c2cf6d9cca38d7323bf2682.jpg'
        },
        {
            title: '【离垢者肃心旅宴】刻晴 44s 8050 永劫龙兽（纪念）',
            bv: 'BV1Qs4y1C71q',
            date: '2023-06-26',
            cover: '0dd5aeb2c07cf34921750373a6a57f0c04591507.jpg'
        },
        {
            title: '【风来人2/离垢者】低配！黎明神剑刻晴8050分龙蜥 无五星武器 无草神',
            bv: 'BV11W4y1Q7Ai',
            date: '2023-06-19',
            cover: '371eb82645f3cec9e8ab8f2d332d2ab5f767f102.jpg'
        },
        {
            title: '【风来人v2】全网首发！刻晴主c无药8050分雷音权现',
            bv: 'BV1Dh411T7J1',
            date: '2023-06-14',
            cover: 'b3f1aa494fc4fcfaff3850ce70382b2e2d6c4422.jpg'
        },
        {
            title: '【3.7深渊】圣骸什么档次？刻草双人78s无伤4圣骸',
            bv: 'BV1H14y1D7HN',
            date: '2023-06-03',
            cover: '65a408914a22f0041dafb4f79fcf5ee4f4ff9a54.jpg'
        },
        {
            title: '【3.5深渊】无敌帧的力量！刻晴队禁移动闪避 无伤12层下半',
            bv: 'BV12V4y1D7Xh',
            date: '2023-03-27',
            cover: '194332de7f2bbf504a6fdb8e32accef7412457a6.jpg'
        },
        {
            title: '【3.4深渊】璃月雷神刻晴11s瞬秒三剑鬼！',
            bv: 'BV1CY411e7Yi',
            date: '2023-02-15',
            cover: 'b5c527d76737d7d3be5cb10dbbfa41d45c783914.jpg'
        },
        {
            title: '「3.4深渊」玉皇妲帝禁移动禁闪避无伤12层上半',
            bv: 'BV1DM4y1X7KQ',
            date: '2023-02-05',
            cover: 'fef08d5b0c928177d782ad8542e23fa293503fc8.jpg'
        },
        {
            title: '「3.3深渊」刻晴草神双人 开盾前一波打死黄金王兽',
            bv: 'BV1Ms4y1x7YQ',
            date: '2023-01-31',
            cover: '343cae61b2e081fda98b55ceb7965ec22cefc048.jpg'
        },
        {
            title: '「3.3深渊」黎明神剑刻晴单c秒黄金王兽',
            bv: 'BV1zy4y1d7ac',
            date: '2023-01-24',
            cover: '0f91eae20a9c2bbd8372fbfa3ab161a1bc72a4bb.jpg'
        },
        {
            title: '「3.3深渊」璃月雷神也要撅大便龙！刻晴18s黄金王兽',
            bv: 'BV1Td4y177dQ',
            date: '2023-01-12',
            cover: 'aae5946c35bc3f207ddcada635a71f070c3434f2.jpg'
        },
        {
            title: '【无相交响诗】璃月雷神又来了！刻晴53s极限无相之草',
            bv: 'BV1WG4y1G7Sg',
            date: '2022-11-29',
            cover: 'a8dd574b605d2700b64ceaa60263e8b1a1a3a4bc.jpg'
        },
        {
            title: '【无相交响诗】璃月雷神归来！刻晴34s极限无相之水',
            bv: 'BV1KK411R7Ne',
            date: '2022-11-27',
            cover: 'da2f635b1bf1fc70b0f1dfbf0b36176d21f97fd9.jpg'
        },
        {
            title: '「3.2深渊」开服常驻永不言败！刻九万妲67秒12层上半三连打',
            bv: 'BV1Q3411f7j5',
            date: '2022-11-22',
            cover: '5db0168b179a96ad98949cf69302381aa9c3a243.jpg'
        },
        {
            title: '「3.1深渊」刻晴12-2 上半10s 下半24s',
            bv: 'BV11K411o7wY',
            date: '2022-11-13',
            cover: 'f37e85a2971d53bb31357d8739b343b1d1368c00.jpg'
        },
        {
            title: '「3.1深渊」刻晴草神激化队39秒12-2上下全间',
            bv: 'BV1Re4y1s7hB',
            date: '2022-11-03',
            cover: '2f58ee9d2fac24326a64a4df0c0537c2a5d02520.jpg'
        },
        {
            title: '「3.1深渊」玉皇妲帝26秒222万妙脆角',
            bv: 'BV1eK411S75w',
            date: '2022-11-03',
            cover: '2440640355e4d5de086399a2a34e412c6aa4af68.jpg'
        },
        {
            title: '【3.1马斯克礁杯】一镜单挑440秒 甘雨x刻晴',
            bv: 'BV1dg41187Fk',
            date: '2022-10-22',
            cover: '08056d3fcc8e30c784603d87ddbe3dc3eee02836.jpg'
        },
        {
            title: '「3.1深渊」一位七星95s单通了222万妙脆角，这是她的动作发生的变化',
            bv: 'BV1xe4y1E7Z8',
            date: '2022-10-14',
            cover: 'eca1c1173e660304963d4c95cb60a6c7250c7e0e.jpg'
        },
        {
            title: '「3.1深渊」一位七星31s打死了222万妙脆角，这是她的伤害发生的变化',
            bv: 'BV1PN4y1w7jk',
            date: '2022-10-14',
            cover: '64a74587c9868caad87a40da9f079992c12e68be.jpg'
        },
        {
            title: '「3.0深渊」刻晴23秒194万血12-3草鸡',
            bv: 'BV1cT411F7s3',
            date: '2022-09-10',
            cover: '1c95c065754d307488627be09e188481e1c8abcc.jpg'
        },
        {
            title: '「2.8深渊」刻晴16s巨蛇 可15s',
            bv: 'BV1ta411K7wA',
            date: '2022-08-04',
            cover: '629f20a93d3b7e74eb7100f5c0f87bd147f98b80.jpg'
        },
        {
            title: '「2.8深渊」刻晴+甘雨单挑满星12-3',
            bv: 'BV17S4y1t7WJ',
            date: '2022-07-30',
            cover: '480c792d63ceffee701935d65b12413d247e199c.jpg'
        },
        {
            title: '「2.8深渊」烟绯+刻晴单挑满星12-3',
            bv: 'BV1Pr4y1j7yB',
            date: '2022-07-30',
            cover: 'cbbb13837115c1510bbbc300df99949ba340d302.jpg'
        },
        {
            title: '「2.7深渊」烟绯+刻晴单挑满星12-3',
            bv: 'BV1rU4y1D7hn',
            date: '2022-07-10',
            cover: 'fcc07b18c04ff93d09eb2431309ba5a51c2d12c6.jpg'
        },
        {
            title: '刻晴4重击秒148万雷神周本 占比68.4%',
            bv: 'BV13a411n79a',
            date: '2022-07-10',
            cover: 'f5f1d32669bcbbc6cceb47543868e33c52a63094.jpg'
        },
        {
            title: '「2.7深渊」27.6词条刻晴79s单挑无相铁（可77）',
            bv: 'BV1fB4y1p7Qu',
            date: '2022-07-01',
            cover: 'c4a1964b064e5d5058d6f1daecc7b6663766beed.jpg'
        },
        {
            title: '刻晴单人1钻地打死遗迹巨蛇',
            bv: 'BV1u3411u741',
            date: '2022-06-19',
            cover: '1f3194f74d3856a709792c052269f1b8ac320c7b.jpg'
        },
        {
            title: '「2.7深渊」刻晴单人108秒无相铁',
            bv: 'BV19L4y1K7yA',
            date: '2022-06-06',
            cover: '9bf9407a10def7420eea76c6080b84caa856bac1.jpg'
        },
        {
            title: '刻晴裟罗 10秒遗迹巨蛇 12秒双子龙蜥',
            bv: 'BV1rU4y197ab',
            date: '2022-06-06',
            cover: '21391eb67febc9b78be9049965d44a1c6bc7ae88.jpg'
        },
        {
            title: '「2.7深渊」刻晴队63秒恒常机关阵列（随便打打）',
            bv: 'BV1pv4y1w7hQ',
            date: '2022-06-01',
            cover: 'e5ef47355c6fd0120cb8fb1ee6cbe9cf786afec6.jpg'
        },
        {
            title: '「2.7深渊」刻晴单人100%守塔 11-1上半',
            bv: 'BV1nU4y1y7wn',
            date: '2022-06-01',
            cover: '6d030b7e9c87aeeb17f5a327e7664d7b711a5e62.jpg'
        },
        {
            title: '「2.6深渊」紫凤起舞！刻晴100s单人无伤双火深渊咏者！',
            bv: 'BV18R4y1P7xX',
            date: '2022-05-03',
            cover: '72a1ac1a21719f720701a6c6b343e2540fa2a160.jpg'
        },
        {
            title: '不到200%暴伤的璃月雷神带队⚡15秒⚡干掉稻妻雷神',
            bv: 'BV1Jr4y1H7bL',
            date: '2022-04-16',
            cover: '7026ed7ef09c37686c6215ffd44273dcead2d1fa.jpg'
        },
        {
            title: '「2.6深渊」刻晴单人100%守护11-1上半',
            bv: 'BV1494y1o77X',
            date: '2022-03-31',
            cover: '1f3194f74d3856a709792c052269f1b8ac320c7b.jpg'
        },
        {
            title: '「2.5深渊」刻晴单人无伤11-3六只流血狗',
            bv: 'BV1T3411s7AB',
            date: '2022-03-16',
            cover: '9323b997a0990e43cbd47a5e8468ef16bbc06e97.jpg'
        },
        {
            title: '「2.5深渊」刻晴12-2上半14秒',
            bv: 'BV1TP4y137aV',
            date: '2022-03-09',
            cover: '1f3194f74d3856a709792c052269f1b8ac320c7b.jpg'
        },
        {
            title: '「2.5深渊」刻晴12-3上半9秒',
            bv: 'BV1hu411B7Yq',
            date: '2022-03-09',
            cover: '1f3194f74d3856a709792c052269f1b8ac320c7b.jpg'
        },
        {
            title: '「2.4深渊」心有所向，永不退环境！3+1刻晴31秒12-3上半',
            bv: 'BV1f34y1k7kp',
            date: '2022-02-09',
            cover: '88cf7785d42b92651075012c093f4dd6a643ac53.jpg'
        },
        {
            title: '「2.4深渊」遗迹机兵就这？刻晴单人100%守塔11-1上半',
            bv: 'BV12r4y1v7oz',
            date: '2022-01-15',
            cover: '2f0d9de6fe28c927bb18dc5360c45503f4f7870f.jpg'
        },
        {
            title: '「2.3深渊」无风系聚怪！刻晴单人守塔100%',
            bv: 'BV1734y1R78Q',
            date: '2021-12-04',
            cover: '75e13da23dae98994462adb585a7e5f157361fa3.jpg'
        },
        {
            title: '「2.3深渊」刻晴单人11-1上 100%',
            bv: 'BV1Cb4y1B7YV',
            date: '2021-11-30',
            cover: '333f866e5c687c7ac3c05c1d9656f9e463f21635.jpg'
        },
        {
            title: '「2.1深渊」刻晴+3星武器万叶双人20秒无伤12-3上半',
            bv: 'BV1iq4y1V7oo',
            date: '2021-10-09',
            cover: '54133006d83cd46cf7673ecdef523fb23d95f763.jpg'
        },
        {
            title: '「2.1深渊」刻晴万叶双人30秒无伤12-3上半',
            bv: 'BV1Vf4y1c7DX',
            date: '2021-10-08',
            cover: 'bbf1af3b07f425d3ccd9dba1bcd1f364e71e84b9.jpg'
        },
        {
            title: '「2.1深渊」刻万温钟29秒12-1上半',
            bv: 'BV1wQ4y1C7jH',
            date: '2021-09-26',
            cover: '35ce2a011168d41700d0aca5dfc49fe5d738509d.jpg'
        },
        {
            title: '阿晴啊，你已经长大了，要学会无伤单挑稻妻天赋本了',
            bv: 'BV1Fy4y1G7Vq',
            date: '2021-08-26',
            cover: '8f4f880e8d745f67ce2fd637d38419a352440645.jpg'
        },
        {
            title: '前方高帅！刻晴单人无伤孤云阁F4',
            bv: 'BV1nh411z7Qv',
            date: '2021-07-30',
            cover: '04efa15a12647a95f67ea6df2d9eb251a51aa1b6.jpg'
        },
        {
            title: '「1.6深渊」刻晴甘雨双人满星11-3',
            bv: 'BV13g41177kP',
            date: '2021-07-30',
            cover: 'e2a6664560a80351b720d502a724bf55affb08e1.jpg'
        },
        {
            title: '「1.6深渊」刻晴甘雨双人满星11-2',
            bv: 'BV1yf4y157hd',
            date: '2021-07-30',
            cover: '83c3ad73bd98a92e32902ab778cd047fe954a2af.jpg'
        },
        {
            title: '「1.6深渊」刻晴单人11-1下半双无伤',
            bv: 'BV1i341167iF',
            date: '2021-07-29',
            cover: 'a2e471e13fe5a31a871d6917a206aab539ca4ed9.jpg'
        },
        {
            title: '「1.6深渊」刻晴单人11-1上半98%',
            bv: 'BV1wL411n7W9',
            date: '2021-07-29',
            cover: '04bbd5c77c3ac4246a1307bff3cd56a86f09f00e.jpg'
        },
        {
            title: '「1.5深渊」物理刻晴一队满星12层',
            bv: 'BV12B4y1T7AU',
            date: '2021-06-10',
            cover: 'dc2167c977ca72483046b87ea6a1455782542333.jpg'
        },
        {
            title: '「1.5深渊」刻晴甘雨双人两分钟通关11-2',
            bv: 'BV17U4y1L7HZ',
            date: '2021-05-29',
            cover: 'fd4a6c0bf7475bd4a1b040cd15377a2c85da43c6.jpg'
        },
        {
            title: '阿晴啊，你已经长大了，要学会单人无伤岩本了',
            bv: 'BV1Z54y1V7nj',
            date: '2021-05-24',
            cover: '0f5360a5617e7e51707e485e17cbf5860b883771.jpg'
        },
        {
            title: '阿晴啊，你已经长大了，要学会独自一人给甘雨姐姐刷圣遗物了',
            bv: 'BV1MU4y1L7wj',
            date: '2021-05-23',
            cover: '2aae8bb23d12dbe441ddf09e6c78a7cac9b65993.jpg'
        },
        {
            title: '阿晴啊，你已经长大了，要学会单挑华池岩岫了',
            bv: 'BV1nf4y1Y7sk',
            date: '2021-05-23',
            cover: '5cdbaa668f66fb8bd14175c42d97391913e7b96a.jpg'
        },
        {
            title: '阿晴啊，你已经长大了，要学会单挑孤云阁F4了',
            bv: 'BV1EK4y1G7fP',
            date: '2021-05-23',
            cover: '7a5c5cd5023c746a25f5b79881c1f4d086e05c4a.jpg'
        },
        {
            title: '无圣遗物刻晴单人通关90级公子',
            bv: 'BV1Ub4y1f7jA',
            date: '2021-05-23',
            cover: 'b0d8eeeb93f78f699534acd013a1f01864bdd862.jpg'
        },
        {
            title: '1级1星武器刻晴单人通关90级公子',
            bv: 'BV11V411j74C',
            date: '2021-05-23',
            cover: '5b4c97b5dc42a776e100bbd04c0c69efc503e851.jpg'
        },
        {
            title: '「1.5深渊」刻晴+魈 11-1 100%',
            bv: 'BV1mV411J7vo',
            date: '2021-05-02',
            cover: 'a0d2d339d1b4b2a7b13159753bdf9d5843a35a24.jpg'
        }
    ]

    var tip = `在 <b>${days}</b> 天前的2021年5月2日，我在bilibili发布了我的第一部刻晴视频<br>多年后的今天，我仍在与刻晴同行；这个页面记录着这些年我发的刻晴视频；这些都是我自己的刻晴留下的足迹`

    $('container').render({
        template: {
            div: [
                {
                    p: '妮可少女的刻晴足迹',
                    class: 'sch_2'
                },
                {
                    p: tip,
                    class: 'avd tip2',
                    style: {
                        margin: '0 8px 14px',
                        'font-weight': 'normal',
                        'text-align': 'center',
                        'line-height': '1.7'
                    }
                },
                {
                    p: computer_.MiscText.Chart_Subtitle[lang],
                    class: 'avd avd_1',
                    style: {
                        'color': '#0066FF',
                        'font-weight': 'bold',
                        'text-align': 'center',
                        'margin-bottom': '13px',
                        'margin-top': '13px'
                    }
                },
                {
                    div: [],
                    class: 'blessing_card_area'
                }
            ],
            class: 'content'
        }
    })

    for (const item of Keqing_Data) {
        $('.blessing_card_area').render({
            div: [
                {
                    a: (window.innerWidth > 500) ? `//www.bilibili.com/video/${item.bv}` : `//player.bilibili.com/player.html?bvid=${item.bv}`,
                    t: {
                        img: `https://homdgcat.wiki/images/cover/${item.cover}`,
                        class: 'item_img'
                    },
                    class: 'item_left',
                    attr: { target: '_blank' }
                },
                {
                    div: [
                        {
                            a: (window.innerWidth > 500) ? `//www.bilibili.com/video/${item.bv}` : `//player.bilibili.com/player.html?bvid=${item.bv}`,
                            t: item.title.replaceAll('【', '「').replaceAll('】', '」'),
                            class: 'item_title',
                            attr: { target: '_blank' }
                        },
                        {
                            p: item.date,
                            class: 'item_date'
                        }
                    ],
                    class: 'item_right'
                }
            ],
            class: 'item'
        })
    }

    if (!lazy) {
        $('body').addClass('bg_3')
        a_section_white()
    } else {
        $('body').addClass('bg')
    }

    console.log("FINISH")

})