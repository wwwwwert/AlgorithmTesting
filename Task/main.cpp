#include <iostream>

using std::cin, std::cout;

long long binPow(long long a, long long n) {
    if (n == 0) {
        return 1;
    }
    if (n % 2 == 1) {
        return binPow(a, n-1) * a;
    } else {
        long long b = binPow(a, n/2);
        return b * b;
    }
}

void RunMain() {
    long long number, power;
    cin >> number >> power;
    cout << binPow(number, power) << '\n';
}

int main() {
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);
    RunMain();
    return 0;
}