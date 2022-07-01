package com.example.mybatisplustest.controller;

import com.example.mybatisplustest.entity.User;
import com.example.mybatisplustest.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/user")
public class UserController {

    @Autowired
    private UserService userService;

    @GetMapping("/hello")
    public String hello() {
        return "Hello World";
    }

    @GetMapping("/findAll")
    public List<User> findAll() {
        return userService.list();
    }

    @GetMapping("/filter")
    public List<User> filter() {
        return userService.likeName();
    }

    @GetMapping("/getUser/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.getById(id);
    }

    @GetMapping("/getUserWithUserLogs/{id}")
    public User getUserWithUserLogs(@PathVariable Long id) {
        return userService.getUserWithUserLogs(id);
    }

    @Deprecated
    @GetMapping("/getUserListWithUserLogs/{id}")
    public List<User> getUserListWithUserLogs(@PathVariable Long id) {
        return userService.getUserListWithUserLogs(id);
    }

    @PostMapping("/insertUser")
    public void insertUser(@RequestBody User user) {
        userService.save(user);
    }

    @PostMapping("/insertUserWithUserLog")
    public void insertUserWithUserLog(@RequestBody User user) throws Exception {
        userService.insertUserWithUserLog(user);
    }

    @PostMapping("/updateUser")
    public void updateUser(@RequestBody User user) {
        userService.updateById(user);
    }

    @GetMapping("/deleteUser/{id}")
    public void deleteUser(@PathVariable Long id) {
        userService.removeById(id);
    }
}
