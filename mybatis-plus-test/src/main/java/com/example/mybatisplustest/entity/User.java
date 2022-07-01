package com.example.mybatisplustest.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.util.Date;
import java.util.List;

@Data
@TableName("tbUser")
public class User {
    @TableId()
    private Long id;
    private String name;
    private Date createTime;
    private Date updateTime;

    @TableField(exist = false)
    private List<UserLog> userLogList;
}
