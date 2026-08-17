Hey team,

昨天跑长途，车载音乐助手在“夜驾驶”播放列表里一直循环同一首歌，简直让人崩溃！我让后端拉了一下 `data/playlists/playlists.json` 和 `data/songs/songs.json`，怀疑是某些播放列表的歌曲 ID 写重了。现在需要你帮忙排查一下所有播放列表，找出那些歌曲 ID 有重复的列表，然后把结果整理成一份报告放在 `ops/` 目录下，文件名叫 `duplicate_songs_report.json`。报告里只需要列出有问题的播放列表 ID 和对应的重复歌曲 ID 列表就行，别的不需要。先谢了！

—— 产品经理 老张
