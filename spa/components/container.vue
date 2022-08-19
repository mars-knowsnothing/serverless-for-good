<template>
    <div class="common-layout">
        <el-container>
            <el-container>
                <!-- <el-aside width="200px">
                    <h3 class="mb-2">Instance Scheduler</h3>
                    <el-menu default-active="1" class="el-menu-vertical-demo" @open="handleOpen" @close="handleClose">
                        <el-menu-item index="1">
                            <el-icon>
                                <icon-menu />
                            </el-icon>
                            <span>Rules</span>
                        </el-menu-item>
                    </el-menu>
                </el-aside> -->
                <el-main>
                    <h2>Instance Scheduler</h2>
                    <Datatable />
                </el-main>
            </el-container>
        </el-container>
    </div>
</template>
