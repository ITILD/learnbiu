/*
 * C++ 进阶语法学习示例
 * 本文件展示了 C++ 的智能指针、模板、RAII 等进阶概念
 * 编译: g++ -std=c++20 -o main_middle main_middle.cpp
 */

#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <map>
#include <functional>

// =============================================================================
// 1. 智能指针示例
// =============================================================================

class Resource
{
private:
    std::string name;

public:
    explicit Resource(std::string n) : name{std::move(n)}
    {
        std::cout << "  [构造] 资源 '" << name << "' 已创建" << std::endl;
    }

    ~Resource()
    {
        std::cout << "  [析构] 资源 '" << name << "' 已释放" << std::endl;
    }

    void use() const
    {
        std::cout << "  [使用] 资源 '" << name << "' 正在使用中" << std::endl;
    }
};

void unique_ptr_examples()
{
    std::cout << "=== std::unique_ptr 独占所有权 ===" << std::endl;

    {
        auto res = std::make_unique<Resource>("数据库连接");
        res->use();
        // 出作用域自动释放
    }
    std::cout << "  ← res 已在上面出作用域时自动释放\n"
              << std::endl;

    // 所有权转移
    auto owner1 = std::make_unique<Resource>("文件句柄");
    owner1->use();

    auto owner2 = std::move(owner1);  // 所有权转移
    // owner1 现在为 nullptr
    std::cout << "  owner1 是否为空: " << (owner1 ? "否" : "是（所有权已转移）") << std::endl;
    owner2->use();
    std::cout << std::endl;
}

void shared_ptr_examples()
{
    std::cout << "=== std::shared_ptr 共享所有权 ===" << std::endl;

    {
        auto s1 = std::make_shared<Resource>("共享缓存");
        std::cout << "  引用计数: " << s1.use_count() << std::endl;

        {
            auto s2 = s1;  // 共享所有权
            std::cout << "  引用计数: " << s1.use_count() << std::endl;

            {
                auto s3 = s2;
                std::cout << "  引用计数: " << s1.use_count() << std::endl;
                s3->use();
            }
            std::cout << "  s3 离开作用域，引用计数: " << s1.use_count() << std::endl;
        }
        std::cout << "  s2 离开作用域，引用计数: " << s1.use_count() << std::endl;
        s1->use();
    }
    std::cout << "  s1 离开作用域，资源释放\n"
              << std::endl;
}

void weak_ptr_examples()
{
    std::cout << "=== std::weak_ptr 弱引用 ===" << std::endl;

    std::weak_ptr<Resource> weak;

    {
        auto shared = std::make_shared<Resource>("弱引用目标");
        weak = shared;

        std::cout << "  shared 引用计数: " << shared.use_count() << std::endl;
        std::cout << "  weak 不增加计数，计数依然是: " << shared.use_count() << std::endl;

        // 使用 lock() 安全访问
        if (auto sp = weak.lock())
        {
            sp->use();
        }
    }

    // shared 已释放，weak.lock() 返回 nullptr
    if (auto sp = weak.lock())
    {
        sp->use();
    }
    else
    {
        std::cout << "  weak.lock() 返回空 — 资源已被释放" << std::endl;
    }
    std::cout << std::endl;
}

// =============================================================================
// 2. 循环引用打破示例
// =============================================================================

class NodeB;  // 前向声明

class NodeA
{
public:
    std::shared_ptr<NodeB> ptr_b;
    ~NodeA() { std::cout << "  [析构] NodeA" << std::endl; }
};

class NodeB
{
public:
    std::weak_ptr<NodeA> ptr_a;  // ← 使用 weak_ptr 打破循环！
    ~NodeB() { std::cout << "  [析构] NodeB" << std::endl; }
};

void cycle_break_example()
{
    std::cout << "=== 打破循环引用 ===" << std::endl;

    auto a = std::make_shared<NodeA>();
    auto b = std::make_shared<NodeB>();

    a->ptr_b = b;
    b->ptr_a = a;  // 因为 weak_ptr，不会阻止释放

    std::cout << "  即使相互引用，离开作用域也能正确释放:" << std::endl;
}

// =============================================================================
// 3. 模板示例
// =============================================================================

template <typename T>
T max_val(T a, T b)
{
    return (a > b) ? a : b;
}

template <typename T>
class SimpleStack
{
private:
    std::vector<T> data;

public:
    void push(const T& val) { data.push_back(val); }

    T pop()
    {
        T top = data.back();
        data.pop_back();
        return top;
    }

    bool empty() const { return data.empty(); }
    size_t size() const { return data.size(); }
};

void template_examples()
{
    std::cout << "=== 模板 ===" << std::endl;

    // 函数模板
    std::cout << "max(3, 5) = " << max_val(3, 5) << std::endl;
    std::cout << "max(3.14, 2.71) = " << max_val(3.14, 2.71) << std::endl;
    std::cout << "max(\"xyz\", \"abc\") = " << max_val(std::string{"xyz"}, std::string{"abc"}) << std::endl;

    // 类模板
    SimpleStack<int> int_stack;
    int_stack.push(10);
    int_stack.push(20);
    int_stack.push(30);

    std::cout << "栈大小: " << int_stack.size() << std::endl;
    while (!int_stack.empty())
    {
        std::cout << "弹出: " << int_stack.pop() << std::endl;
    }
    std::cout << std::endl;
}

// =============================================================================
// 4. RAII 模式示例
// =============================================================================

class FileGuard
{
private:
    std::string path;
    bool is_open{false};

public:
    explicit FileGuard(std::string p) : path{std::move(p)}
    {
        is_open = true;
        std::cout << "  [RAII] 打开文件: " << path << std::endl;
    }

    ~FileGuard()
    {
        if (is_open)
        {
            std::cout << "  [RAII] 关闭文件: " << path << std::endl;
        }
    }

    void write(const std::string& content)
    {
        std::cout << "  [RAII] 写入 '" << content << "' 到 " << path << std::endl;
    }

    // 禁止拷贝
    FileGuard(const FileGuard&) = delete;
    FileGuard& operator=(const FileGuard&) = delete;

    // 允许移动
    FileGuard(FileGuard&& other) noexcept
        : path{std::move(other.path)}, is_open{other.is_open}
    {
        other.is_open = false;
    }
};

void raii_example()
{
    std::cout << "=== RAII 资源管理 ===" << std::endl;

    {
        FileGuard file{"output.txt"};
        file.write("Hello, RAII!");
        // 即使这里抛异常，析构函数也会执行
    }
    std::cout << "  ← 文件已在析构时自动关闭\n"
              << std::endl;
}

// =============================================================================
// 主函数
// =============================================================================

int main()
{
    std::cout << "═══════════════════════════════════════" << std::endl;
    std::cout << "   C++ 进阶示例：智能指针、模板、RAII" << std::endl;
    std::cout << "═══════════════════════════════════════\n"
              << std::endl;

    unique_ptr_examples();
    shared_ptr_examples();
    weak_ptr_examples();
    cycle_break_example();
    template_examples();
    raii_example();

    std::cout << "✅ 所有进阶示例执行完成！" << std::endl;
    std::cout << "💡 关键建议：默认使用 unique_ptr，需要共享时用 shared_ptr" << std::endl;
    std::cout << "💡 使用 RAII 模式管理所有资源（内存、文件、锁等）" << std::endl;

    return 0;
}