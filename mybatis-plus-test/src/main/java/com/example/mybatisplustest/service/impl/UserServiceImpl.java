package com.example.mybatisplustest.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.mybatisplustest.entity.User;
import com.example.mybatisplustest.entity.UserLog;
import com.example.mybatisplustest.mapper.UserLogMapper;
import com.example.mybatisplustest.mapper.UserMapper;
import com.example.mybatisplustest.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {

    @Autowired
    private UserMapper userMapper;

    @Autowired
    private UserLogMapper userLogMapper;

    @Override
    public List<User> likeName() {
        QueryWrapper<User> queryWrapper = new QueryWrapper<>();
        queryWrapper.likeRight("Name", "update");
        return userMapper.selectList(queryWrapper);
    }

    @Override
    public User getUserWithUserLogs(Long id) {
        QueryWrapper<UserLog> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("UserId", id);
        List<UserLog> userLogList = userLogMapper.selectList(queryWrapper);
        User userWithUserLogs = userMapper.selectById(id);
        userWithUserLogs.setUserLogList(userLogList);
        return userWithUserLogs;
    }

    @Override
    public List<User> getUserListWithUserLogs(Long id) {
        return userMapper.getUserListWithUserLogs(id);
    }

    @Override
    @Transactional(rollbackFor = Exception.class) // Exception及其子类均适用
    public void insertUserWithUserLog(User user) throws Exception {
        userMapper.insert(user);

        UserLog userLog = new UserLog();
        userLog.setUserId(user.getId());
        userLog.setName(user.getName());

        UserLog userLogSql = new UserLog();
        userLogSql.setUserId(user.getId());
        userLogSql.setName("userLogSql");

//        UserLog userLogNull = new UserLog();
//        if (userLogNull.getName() == null) {
//            System.out.println("null");
//            throw new Exception();
////            throw new IndexOutOfBoundsException();
//        }

        userLogMapper.insert(userLog);
//        int a = 1 / 0;
        userLogMapper.insertUserLog(userLogSql);
    }
}
