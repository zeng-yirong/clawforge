**主题: [紧急] 主库IO飙升，需要立即强杀长事务**

兄弟，主库IO飙到100%了！我刚从慢查询日志和pg_locks抓到的信息看，有几个db_replica_lag类型的高危事故未处理，状态还是open。我手头在处理别的，你帮我把`data/incidents/`下的`incident_pool.json`打开，找出所有`category`是`db_replica_lag`、`severity`是`critical`并且`status`是`open`的事故ID。把它们写到一个`ops/kill_target.json`文件里，我用脚本直接强杀。别把那些已经triaged或者非critical的搞进去。快点，再拖下去要出SLA违约了！

另外，注意`ops`目录可能还没建，你自己创建一下。谢了！
