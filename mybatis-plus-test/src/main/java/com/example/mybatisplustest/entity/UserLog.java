package com.example.mybatisplustest.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.util.Date;

@Data
@TableName("tbUserLog")
public class UserLog {
    @TableId()
    private Long id;
    private Long userId;
    private String name;
    private Date createTime;
    private Date updateTime;
}
