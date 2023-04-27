struct Output {
    index: atomic<u32>,
    data: array<u32>
};

@binding(0) @group(0) var<storage, read> input_data: array<u32>;
@binding(1) @group(0) var<storage, read_write> output_data: Output;

@compute
@workgroup_size(4, 4, 16)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
    var seed: u32 = (global_id.x << 22u) | (global_id.y << 12u) | (global_id.z + input_data[1]);

    var s1: u32 = (0x6C078965u * (seed ^ (seed >> 30u))) + 1u;
    var s2: u32 = (0x6C078965u * (s1 ^ (s1 >> 30u))) + 2u;
    var s398: u32 = s2;
    for (var i: u32 = 3u; i < 399u; i++) {
        s398 = (0x6C078965u * (s398 ^ (s398 >> 30u))) + i;
    }

    var y: u32 = (s1 & 0x80000000u) | (s2 & 0x7fffffffu);
    s1 = (s398 ^ (y >> 1u)) ^ ((y & 1u) * 0x9908B0DFu);
    y = s1 ^ (s1 >> 11u);
    y ^= (y << 7u) & 0x9d2c5680u;
    y ^= (y << 15u) & 0xefc60000u;
    y ^= y >> 18u;
    if (y == input_data[0]) {
        output_data.data[atomicAdd(&output_data.index, 1u)] = seed;
    }
}