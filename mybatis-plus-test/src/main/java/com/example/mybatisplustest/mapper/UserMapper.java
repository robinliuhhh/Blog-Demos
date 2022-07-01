package com.example.mybatisplustest.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.mybatisplustest.entity.User;
import org.apache.ibatis.annotations.Select;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface UserMapper extends BaseMapper<User> {

    String withUserLogsSql = "select * from tbUser u left join tbUserLog log on u.id = log.userId where log.userId = #{id}";

    @Deprecated
    // Expected one result (or null) to be returned by selectOne(), but found: 2 => 应返回List<User> 此时不是一对多
    @Select(withUserLogsSql)
    User getUserWithUserLogs(Long id);

    @Deprecated
    // Columns: Id, Name, CreateTime, UpdateTime, Id, UserId, Name, CreateTime, UpdateTime
    // userLogList 注入失败
    @Select(withUserLogsSql)
    List<User> getUserListWithUserLogs(Long id);
}
