/*
 * gl_nullify.c - OpenGL stub library for headless Unity games
 *
 * Compile: gcc -shared -fPIC -o gl_nullify.so gl_nullify.c -ldl
 * Use: LD_PRELOAD=./gl_nullify.so ./hackmud.x86_64
 *
 * This intercepts OpenGL calls and makes them no-ops to reduce CPU
 * when running in a virtual framebuffer (Xvfb) without GPU.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>

// Set to 1 to enable logging of stubbed calls
#define DEBUG_LOG 1

#if DEBUG_LOG
#define LOG(fmt, ...) fprintf(stderr, "[gl_nullify] " fmt "\n", ##__VA_ARGS__)
#else
#define LOG(fmt, ...)
#endif

// Counter for generating fake IDs
static unsigned int fake_id = 1;

// ============ DRAW CALLS (biggest CPU savers) ============

void glDrawArrays(int mode, int first, int count) {
    LOG("glDrawArrays(mode=%d, first=%d, count=%d)", mode, first, count);
}

void glDrawElements(int mode, int count, int type, const void* indices) {
    LOG("glDrawElements(mode=%d, count=%d)", mode, count);
}

void glDrawArraysInstanced(int mode, int first, int count, int instancecount) {
    LOG("glDrawArraysInstanced(count=%d, instances=%d)", count, instancecount);
}

void glDrawElementsInstanced(int mode, int count, int type, const void* indices, int instancecount) {
    LOG("glDrawElementsInstanced(count=%d, instances=%d)", count, instancecount);
}

// ============ BUFFER SWAP ============

void glXSwapBuffers(void* dpy, void* drawable) {
    LOG("glXSwapBuffers");
}

// ============ CLEAR OPERATIONS ============

void glClear(unsigned int mask) {
    LOG("glClear(mask=0x%x)", mask);
}

void glClearColor(float r, float g, float b, float a) {
    LOG("glClearColor(%.2f, %.2f, %.2f, %.2f)", r, g, b, a);
}

// ============ TEXTURE OPERATIONS ============

void glGenTextures(int n, unsigned int* textures) {
    LOG("glGenTextures(n=%d)", n);
    for (int i = 0; i < n; i++) {
        textures[i] = fake_id++;
    }
}

void glDeleteTextures(int n, const unsigned int* textures) {
    LOG("glDeleteTextures(n=%d)", n);
}

void glBindTexture(int target, unsigned int texture) {
    LOG("glBindTexture(target=0x%x, texture=%u)", target, texture);
}

void glTexImage2D(int target, int level, int internalformat, int width, int height,
                  int border, int format, int type, const void* data) {
    LOG("glTexImage2D(%dx%d)", width, height);
}

void glTexSubImage2D(int target, int level, int xoffset, int yoffset,
                     int width, int height, int format, int type, const void* data) {
    LOG("glTexSubImage2D(%dx%d)", width, height);
}

// ============ BUFFER OPERATIONS ============

void glGenBuffers(int n, unsigned int* buffers) {
    LOG("glGenBuffers(n=%d)", n);
    for (int i = 0; i < n; i++) {
        buffers[i] = fake_id++;
    }
}

void glDeleteBuffers(int n, const unsigned int* buffers) {
    LOG("glDeleteBuffers(n=%d)", n);
}

void glBindBuffer(int target, unsigned int buffer) {
    LOG("glBindBuffer(target=0x%x, buffer=%u)", target, buffer);
}

void glBufferData(int target, long size, const void* data, int usage) {
    LOG("glBufferData(size=%ld)", size);
}

void glBufferSubData(int target, long offset, long size, const void* data) {
    LOG("glBufferSubData(size=%ld)", size);
}

// ============ SHADER OPERATIONS ============

unsigned int glCreateShader(int type) {
    LOG("glCreateShader(type=0x%x) -> %u", type, fake_id);
    return fake_id++;
}

void glDeleteShader(unsigned int shader) {
    LOG("glDeleteShader(%u)", shader);
}

void glShaderSource(unsigned int shader, int count, const char** string, const int* length) {
    LOG("glShaderSource(shader=%u)", shader);
}

void glCompileShader(unsigned int shader) {
    LOG("glCompileShader(%u)", shader);
}

unsigned int glCreateProgram(void) {
    LOG("glCreateProgram() -> %u", fake_id);
    return fake_id++;
}

void glDeleteProgram(unsigned int program) {
    LOG("glDeleteProgram(%u)", program);
}

void glAttachShader(unsigned int program, unsigned int shader) {
    LOG("glAttachShader(prog=%u, shader=%u)", program, shader);
}

void glLinkProgram(unsigned int program) {
    LOG("glLinkProgram(%u)", program);
}

void glUseProgram(unsigned int program) {
    LOG("glUseProgram(%u)", program);
}

// ============ VAO OPERATIONS ============

void glGenVertexArrays(int n, unsigned int* arrays) {
    LOG("glGenVertexArrays(n=%d)", n);
    for (int i = 0; i < n; i++) {
        arrays[i] = fake_id++;
    }
}

void glDeleteVertexArrays(int n, const unsigned int* arrays) {
    LOG("glDeleteVertexArrays(n=%d)", n);
}

void glBindVertexArray(unsigned int array) {
    LOG("glBindVertexArray(%u)", array);
}

// ============ STATE CHANGES ============

void glEnable(int cap) {
    LOG("glEnable(0x%x)", cap);
}

void glDisable(int cap) {
    LOG("glDisable(0x%x)", cap);
}

void glBlendFunc(int sfactor, int dfactor) {
    LOG("glBlendFunc(0x%x, 0x%x)", sfactor, dfactor);
}

void glViewport(int x, int y, int width, int height) {
    LOG("glViewport(%d, %d, %d, %d)", x, y, width, height);
}

void glScissor(int x, int y, int width, int height) {
    LOG("glScissor(%d, %d, %d, %d)", x, y, width, height);
}

// ============ FRAMEBUFFER OPERATIONS ============

void glGenFramebuffers(int n, unsigned int* framebuffers) {
    LOG("glGenFramebuffers(n=%d)", n);
    for (int i = 0; i < n; i++) {
        framebuffers[i] = fake_id++;
    }
}

void glDeleteFramebuffers(int n, const unsigned int* framebuffers) {
    LOG("glDeleteFramebuffers(n=%d)", n);
}

void glBindFramebuffer(int target, unsigned int framebuffer) {
    LOG("glBindFramebuffer(target=0x%x, fb=%u)", target, framebuffer);
}

int glCheckFramebufferStatus(int target) {
    LOG("glCheckFramebufferStatus -> GL_FRAMEBUFFER_COMPLETE");
    return 0x8CD5;  // GL_FRAMEBUFFER_COMPLETE
}

// ============ QUERY FUNCTIONS (need valid returns) ============

void glGetIntegerv(int pname, int* params) {
    LOG("glGetIntegerv(pname=0x%x)", pname);
    // Return safe default values
    if (params) *params = 1;
}

const unsigned char* glGetString(int name) {
    LOG("glGetString(name=0x%x)", name);
    static const char* vendor = "GL Nullify";
    static const char* renderer = "Null Renderer";
    static const char* version = "4.5";
    static const char* extensions = "";

    switch(name) {
        case 0x1F00: return (const unsigned char*)vendor;    // GL_VENDOR
        case 0x1F01: return (const unsigned char*)renderer;  // GL_RENDERER
        case 0x1F02: return (const unsigned char*)version;   // GL_VERSION
        case 0x1F03: return (const unsigned char*)extensions; // GL_EXTENSIONS
    }
    return (const unsigned char*)"";
}

int glGetError(void) {
    return 0;  // GL_NO_ERROR
}

void glGetShaderiv(unsigned int shader, int pname, int* params) {
    LOG("glGetShaderiv(shader=%u, pname=0x%x)", shader, pname);
    if (params) {
        if (pname == 0x8B81) *params = 1;  // GL_COMPILE_STATUS = success
        else *params = 0;
    }
}

void glGetProgramiv(unsigned int program, int pname, int* params) {
    LOG("glGetProgramiv(prog=%u, pname=0x%x)", program, pname);
    if (params) {
        if (pname == 0x8B82) *params = 1;  // GL_LINK_STATUS = success
        else *params = 0;
    }
}
