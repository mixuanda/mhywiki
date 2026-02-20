$(function () {
  var imgpre = $('#IMGPRE').val();
  var lazy = $('#NOLAZY').val() ? '' : 'lazy';
  init_title('玉衡杯重现 ' + computer_.MiscText.PAGE_TITLE[lang]);
  $('.tls' + lang).css("color", "#df903b");
  $('h3 .title').html(computer_.MiscText.Title[lang] + "<color style='font-size: 26px;'><br>" + computer_.MiscText.game_img[lang] + VER_GI + "</b></color>");
  $('h3 .subtitle').html(computer_.MiscText.Subtitle[lang]);
  $('h3 .tlsub').html(computer_.MiscText.Translate_);
  $('h3 .tlsub').hide();
  $('h3 .links').render([{
    img: imgpre + 'images/menu.png',
    class: '_menu_'
  }, {
    img: imgpre + 'images/translate.png',
    class: '_translate_'
  }]);
  var cur_time = Date.now();
  var days_1 = Math.round((cur_time - Date.parse('2022-04-01T12:00:00+08:00')) / 86400000).toString();
  var days_2 = Math.round((cur_time - Date.parse('2023-05-09T12:00:00+08:00')) / 86400000).toString();
  var days_3 = Math.round((cur_time - Date.parse('2024-07-16T12:00:00+08:00')) / 86400000).toString();
  var days_4 = Math.round((cur_time - Date.parse('2025-11-20T00:00:00+08:00')) / 86400000).toString();
  var tip = [">>> \u5728 <b>".concat(days_1, "</b> \u5929\u524D\u76842022\u5E744\u67081\u65E5\uFF0C\u7B2C\u4E00\u5C4A\u7389\u8861\u676F\uFF08\u5F53\u65F6\u540D\u4E3A\u523B\u6674\u676F\uFF09\u5F00\u8D5B\uFF0C\u5185\u5BB9\u4E3A <b>2.6</b> \u7248\u672C\u6E0A\u6708\u87BA\u65CB12\u5C42\u7ADE\u901F"), ">>> \u5728 <b>".concat(days_2, "</b> \u5929\u524D\u76842023\u5E745\u67089\u65E5\uFF0C\u7389\u8861\u676F\u7F51\u7AD9\u6B63\u5F0F\u6295\u5165\u4F7F\u7528\uFF0C\u7F51\u7AD9\u8BB0\u5F55\u4E86\u7B2C\u516B\u5C4A\uFF083.5\uFF09\u81F3\u7B2C\u5341\u4E09\u5C4A\uFF084.4\uFF09\u7389\u8861\u676F\u7684\u6570\u636E"), ">>> \u5728 <b>".concat(days_3, "</b> \u5929\u524D\u76842024\u5E747\u670816\u65E5\uFF0C\u6700\u540E\u4E00\u5C4A\u7389\u8861\u676F\uFF1A\u7B2C\u5341\u56DB\u5C4A\u7389\u8861\u676F\uFF084.7\uFF09\u843D\u4E0B\u5E37\u5E55\uFF0C\u6B64\u65F6\u8DDD\u79BB\u7B2C\u4E00\u5C4A\u5F00\u8D5B\u5DF2\u6709 <b>837</b> \u5929"), ">>> \u5728 <b>".concat(days_4, "</b> \u5929\u524D\u76842025\u5E7411\u670820\u65E5\uFF0C\u523B\u6674\u7684\u7B2C\u516D\u6B21\u751F\u65E5\uFF0C\u6211\u7528\u6211\u4FDD\u5B58\u7684\u300C\u8BB0\u5FC6\u300D\u2014\u2014\u8001\u7389\u8861\u676F\u7F51\u7AD9\u7684\u6570\u636E\uFF0C\u91CD\u73B0\u4E86\u7389\u8861\u676F\u7684\u5185\u5BB9")];
  $('container').render({
    template: {
      div: [{
        p: '玉衡杯重现',
        class: 'sch_2'
      }, {
        div: {
          p: tip.join("<br>"),
          class: 'avd tip2',
          style: {
            margin: '0 8px 14px',
            'font-weight': 'normal',
            'line-height': '1.9',
            width: 'max-content',
            'max-width': '100%'
          }
        },
        style: {
          display: 'flex',
          'justify-content': 'center'
        }
      }, {
        div: [{
          schedule: '成绩记录',
          class: 'active',
          click: render_track
        }, {
          schedule: '早期集锦',
          click: render_highlights
        }, {
          schedule: '教程攻略',
          click: render_tutorials
        }, {
          schedule: '规则 讯息',
          click: render_rules
        }],
        class: 'select'
      }, {
        div: [],
        class: 'blessing_card_area'
      }],
      class: 'content'
    }
  });
  render_track();
  function render_track() {
    // Remember NGA also BV1a7421N7cn

    $('.blessing_card_area').empty();
    for (const i in data_tracks) {
      var c_data = data_tracks[data_tracks.length - i - 1];
      var this_competition_info = [];
      var this_competition_info_contents = [{
        scheduled: '收起',
        class: "rule_title cd cd_0 active_2 content_".concat(c_data._id + '_' + '1145'),
        a: {
          'data-id': c_data._id + '_' + '1145'
        }
      }];
      for (const t_data of c_data.tracks) {
        var this_track_info = [{
          tr: [{
            th: '用时',
            class: 'td_text'
          }, {
            th: '阵容',
            class: 'td_text'
          }, {
            th: '视频',
            class: 'td_text'
          }, {
            th: '作者',
            class: 'td_text'
          }, {
            th: '成本',
            class: 'td_text'
          }]
        }];
        var records_temp = t_data.records;
        var unique_id = c_data._id + '_' + t_data._id;
        records_temp.sort(function (a, b) {
          return a.score - b.score;
        });
        for (const r_data of records_temp) {
          var role_avatar = [];
          var role_weapon = [];
          for (const role_data of r_data.role) {
            role_avatar.push({
              a: "/gi/char/".concat(role_data.avatar),
              t: [{
                img: "/homdgcat-res/Avatar/UI_AvatarIcon_".concat(role_data.avatar, ".png")
              }, {
                span: role_data.avatar_num.toString(),
                class: 'ref'
              }],
              attr: {
                target: '_blank'
              },
              class: 'role_single hover-shadow'
            });
            role_weapon.push({
              a: "/gi/char/".concat(role_data.weapon),
              t: [{
                img: "/homdgcat-res/Weapon/".concat(weapon_data[role_data.weapon], ".png")
              }, {
                span: role_data.weapon_num.toString(),
                class: 'ref'
              }],
              attr: {
                target: '_blank'
              },
              class: 'role_single hover-shadow'
            });
          }
          this_track_info.push({
            tr: [{
              td: r_data.score.toString(),
              class: 'td_score'
            }, {
              td: [{
                div: role_avatar,
                class: 'role_wrap role_avatar'
              }, {
                div: role_weapon,
                class: 'role_wrap role_weapon'
              }],
              class: 'td_roles'
            }, {
              td: {
                a: window.innerWidth > 500 ? "//www.bilibili.com/video/".concat(r_data.bv) : "//player.bilibili.com/player.html?bvid=".concat(r_data.bv),
                t: "<u>".concat(r_data.bv, "</u>"),
                attr: {
                  target: '_blank'
                },
                class: 'hover-shadow'
              },
              class: 'td_text'
            }, {
              td: r_data.name,
              class: 'td_text'
            }, {
              td: r_data.cost.toString(),
              class: 'td_score'
            }]
          });
          if (r_data.message) {
            this_track_info.push({
              tr: [{
                td: {
                  p: '留言：' + r_data.message,
                  class: 'td_message'
                },
                a: {
                  colspan: '5'
                }
              }]
            });
          }
        }
        this_competition_info_contents.push({
          scheduled: t_data.name,
          class: "rule_title cd cd_0 content_".concat(unique_id),
          a: {
            'data-id': unique_id
          }
        });
        this_competition_info.push({
          div: [{
            div: {
              table: this_track_info,
              class: 'area_record_table'
            },
            class: 'area_record_table_wrap'
          }],
          class: "area_track cd cd_1 data_".concat(unique_id)
        });
      }
      var shpli = c_data.name.split(' ');
      $('.blessing_card_area').render({
        div: [{
          p: c_data.name,
          class: 'rule_title_big'
        }, {
          p: c_data.time,
          class: 'rule_text'
        }, {
          a: "/gi/abyss/".concat(shpli[shpli.length - 1]),
          t: {
            p: '> 深渊阵容 <',
            class: 'rule_title',
            style: {
              'margin-top': '10px'
            }
          },
          style: {
            color: '#FFD780',
            'text-align': 'center',
            'font-weight': 'bold'
          },
          attr: {
            target: '_blank'
          }
        },
        /*{
            p: '＋ 展开 ＋',
            class: 'hd hd_1 hd_0'
        },
        {
            p: '− 收起 −',
            class: 'hd hd_2 hd_0'
        },*/
        {
          div: this_competition_info_contents,
          class: 'area_track_wrap'
        }, {
          div: this_competition_info,
          class: 'area_track_wrap_2'
        }],
        class: 'card_7'
      });
    }
    $('.cd_1').hide();
  }
  function render_rules() {
    $('.blessing_card_area').empty();
    for (const i in data_rules) {
      var dat = data_rules[data_rules.length - 1 - i];
      var link = '';
      if (dat.url.includes('BV')) {
        link = window.innerWidth > 500 ? "//www.bilibili.com/video/".concat(dat.url) : "//player.bilibili.com/player.html?bvid=".concat(dat.url);
      } else {
        link = "//www.bilibili.com/read/".concat(dat.url);
      }
      $('.blessing_card_area').render({
        a: link,
        t: [{
          p: dat.title,
          class: 'rule_title'
        }, {
          p: dat.update_time,
          class: 'rule_text'
        }],
        class: 'card_9 hover-shadow',
        attr: {
          target: '_blank'
        }
      });
    }
  }
  function render_highlights() {
    $('.blessing_card_area').empty();
    for (const i in data_highlights) {
      var h_data = data_highlights[data_highlights.length - 1 - i];
      for (const i_data of h_data.items) {
        var link = window.innerWidth > 500 ? "//www.bilibili.com/video/".concat(i_data.url) : "//player.bilibili.com/player.html?bvid=".concat(i_data.url);
        $('.blessing_card_area').render({
          a: link,
          t: [{
            p: "<color style='color:rgb(255, 172, 255)'><b>" + h_data.name + "</b></color> " + i_data.title,
            class: 'rule_title'
          }, {
            p: i_data.creator,
            class: 'rule_text',
            style: {
              color: '#FFD780'
            }
          }, {
            div: {
              iframe: '',
              a: {
                src: "//player.bilibili.com/player.html?bvid=".concat(i_data.url, "&isOutside=true&autoplay=0"),
                scrolling: "no",
                border: "0",
                frameborder: "no",
                framespacing: "0",
                allowfullscreen: "true"
              }
            },
            class: 'iframe_container'
          }],
          class: 'card_8',
          attr: {
            target: '_blank'
          }
        });
      }
    }
  }
  function render_tutorials() {
    $('.blessing_card_area').empty();
    for (const i in data_tutorials) {
      var dat = data_tutorials[data_tutorials.length - 1 - i];
      var link = '';
      if (dat.url.includes('BV')) {
        link = window.innerWidth > 500 ? "//www.bilibili.com/video/".concat(dat.url) : "//player.bilibili.com/player.html?bvid=".concat(dat.url);
      } else {
        link = "//www.bilibili.com/read/".concat(dat.url);
      }
      $('.blessing_card_area').render({
        a: link,
        t: [{
          p: dat.title,
          class: 'rule_title'
        }, {
          p: dat.creator,
          class: 'rule_text',
          style: {
            color: '#FFD780'
          }
        }, {
          p: dat.intro,
          class: 'rule_text'
        }],
        class: 'card_9 hover-shadow',
        attr: {
          target: '_blank'
        }
      });
    }
  }
  $('body').on('click', '.select schedule', function () {
    if ($(this).hasClass('active')) return;
    $(this).siblings().removeClass('active');
    $(this).addClass('active');
  });
  $('body').on('click', '.hd_0', function () {
    $(this).toggle();
    $(this).siblings('.hd').toggle();
  });
  if (!lazy) {
    $('body').addClass('bg_3');
    a_section_white();
  } else {
    $('body').addClass('bg');
  }
  $('body').on('click', 'scheduled', function () {
    if ($(this).hasClass('active_2')) return;
    $(this).siblings().removeClass('active_2');
    $(this).addClass('active_2');
    $(this).parent().siblings('.area_track_wrap_2').find('.cd_1').hide();
    $('.data_' + $(this).attr('data-id')).show();
  });
  console.log("FINISH");
});