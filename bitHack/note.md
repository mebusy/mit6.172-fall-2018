# bit ops note

## 计算 integer 符号 (+1,0,-1)

```c
sign = (v > 0) - (v < 0); // -1, 0, or +1
```


## Counting bits set


```c
unsigned int v; // count the number of bits set in v
unsigned int c; // c accumulates the total bits set in v
for (c = 0; v; c++)
{
  v &= v - 1; // clear the least significant bit set
}
```

## Counting bits set in 14, 24, or 32-bit words using 64-bit instructions


```c
unsigned int v; // count the number of bits set in v
unsigned int c; // c accumulates the total bits set in v

// option 1, for at most 14-bit values in v:
c = (v * 0x200040008001ULL & 0x111111111111111ULL) % 0xf;

// option 2, for at most 24-bit values in v:
c =  ((v & 0xfff) * 0x1001001001001ULL & 0x84210842108421ULL) % 0x1f;
c += (((v & 0xfff000) >> 12) * 0x1001001001001ULL & 0x84210842108421ULL) 
     % 0x1f;

// option 3, for at most 32-bit values in v:
c =  ((v & 0xfff) * 0x1001001001001ULL & 0x84210842108421ULL) % 0x1f;
c += (((v & 0xfff000) >> 12) * 0x1001001001001ULL & 0x84210842108421ULL) % 
     0x1f;
c += ((v >> 24) * 0x1001001001001ULL & 0x84210842108421ULL) % 0x1f;
```


## Reverse the bits in a byte with 3 operations (64-bit multiply and modulus division):

```c
unsigned char b; // reverse this (8-bit) byte
b = (b * 0x0202020202ULL & 0x010884422010ULL) % 1023;
```

## Reverse the bits in a byte with 4 operations (64-bit multiply, no division):


```c
unsigned char b; // reverse this byte
b = ((b * 0x80200802ULL) & 0x0884422110ULL) * 0x0101010101ULL >> 32;
```

## Count the consecutive zero bits (trailing) on the right in parallel

```c
unsigned int v;      // 32-bit word input to count zero bits on right
unsigned int c = 32; // c will be the number of zero bits on the right
v &= -signed(v);
if (v) c--;
if (v & 0x0000FFFF) c -= 16;
if (v & 0x00FF00FF) c -= 8;
if (v & 0x0F0F0F0F) c -= 4;
if (v & 0x33333333) c -= 2;
if (v & 0x55555555) c -= 1;
```

## Round up to the next highest power of 2 ( e.g. 54 -> 64)

```c
unsigned int v; // compute the next highest power of 2 of 32-bit v

v--;  // if case v is power of 2
v |= v >> 1; // fill with all 1s from the MSB
v |= v >> 2;
v |= v >> 4;
v |= v >> 8;
v |= v >> 16;
// v |= v >> 32;  // if v is 64-bit
v++;
```

## Floor down to the next lowest power of 2 ( e.g. 54 -> 32)

```c
n |= n >> 1; // fill with all 1s from the MSB
n |= n >> 2;
n |= n >> 4;
n |= n >> 8;
n |= n >> 16;
// n |= n >> 32;  // if n is 64-bit
n &= ~(n >> 1)
```

## log base 2 of an 32-bit integer

```c
uint32_t v; // find the log base 2 of 32-bit v
int r;      // result goes here

static const int MultiplyDeBruijnBitPosition[32] = 
{
  0, 9, 1, 10, 13, 21, 2, 29, 11, 14, 16, 18, 22, 25, 3, 30,
  8, 12, 20, 28, 15, 17, 24, 7, 19, 27, 23, 6, 26, 5, 4, 31
};

v |= v >> 1; // first round down to one less than a power of 2 
v |= v >> 2;
v |= v >> 4;
v |= v >> 8;
v |= v >> 16;

r = MultiplyDeBruijnBitPosition[(uint32_t)(v * 0x07C4ACDDU) >> 27];
```


## Determine if a word has a byte equal to n

```c
#define hasvalue(x,n)  (haszero((x) ^ (~0UL/255 * (n))))
```

## Determine if a word has a byte less than n

Requirements: `x>=0; 0<=n<=128`

```c
#define hasless(x,n) (((x)-~0UL/255*(n))&~(x)&~0UL/255*128)
```

To count the number of bytes in x that are less than n in 7 operations, use

```c
#define countless(x,n)  (((~0UL/255*(127+(n))-((x)&~0UL/255*127))&~(x)&~0UL/255*128)/128%255)
```


## Determine if a word has a byte greater than n

Requirements: `x>=0; 0<=n<=127`

```c
#define hasmore(x,n) (((x)+~0UL/255*(127-(n))|(x))&~0UL/255*128)
```

To count the number of bytes in x that are more than n in 6 operations, use:

```c
#define countmore(x,n)  (((((x)&~0UL/255*127)+~0UL/255*(127-(n))|(x))&~0UL/255*128)/128%255)
```


## Determine if a word has a zero byte

```c
hasless(x,1)
```


