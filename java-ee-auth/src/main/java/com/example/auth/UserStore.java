package com.example.auth;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class UserStore {
    private static final Map<String, User> USERS = new ConcurrentHashMap<>();

    static {
        USERS.put("admin", new User("admin", "admin123"));
        USERS.put("user", new User("user", "user123"));
    }

    public static boolean isValid(String username, String password) {
        User u = USERS.get(username);
        return u != null && u.getPassword().equals(password);
    }

    public static void register(String username, String password) {
        USERS.put(username, new User(username, password));
    }
}
