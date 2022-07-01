package com.example.mybatisplustest.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.example.mybatisplustest.entity.User;

import java.util.List;

public interface UserService extends IService<User> {

    List<User> likeName();

    User getUserWithUserLogs(Long id);

    List<User> getUserListWithUserLogs(Long id);

    void insertUserWithUserLog(User user) throws Exception;
}
