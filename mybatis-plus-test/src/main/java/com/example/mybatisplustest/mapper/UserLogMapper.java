package com.example.mybatisplustest.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.mybatisplustest.entity.UserLog;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Options;
import org.springframework.stereotype.Repository;

@Repository
public interface UserLogMapper extends BaseMapper<UserLog> {

    // ${} 是 Properties 文件中的变量占位符，它可以用于标签属性值和 sql 内部，属于静态文本替换
    // #{} 是 sql 的参数占位符，MyBatis 会将 sql 中的 #{} 替换为? 号
    //     在 sql 执行前会使用 PreparedStatement 的参数设置方法，按序给 sql 的? 号占位符设置参数值
    //     该方式能够很大程度防止 sql 注入

    // tbUserLog(UserId, Name)对应数据库字段 values(#{userId}, #{name})对应entity字段
    @Insert("insert into tbUserLog(UserId, Name) values(#{userId}, #{name})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    void insertUserLog(UserLog userLog);
}